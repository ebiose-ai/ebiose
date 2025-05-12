import logging  # Use logging for warnings/errors
from typing import Any, ForwardRef, Optional, Union

import pydantic
from pydantic import (  # Import Field for potential future use
    BaseModel,
    create_model,
)

# --- Configuration ---
_DEFS_KEY = "$defs" # Pydantic V2 uses $defs
_RECURSION_DEPTH_LIMIT = 20 # Protection against infinite recursion
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Type Mapping ---
# Maps JSON schema types to Python types
TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "null": type(None),
}

# --- Caching (Module Level for a Single Run) ---
# These caches store models created during a single call to the main function.
# They are cleared at the start of each top-level create_pydantic_model_from_schema call.
_MODEL_CACHE: dict[str, type[BaseModel] | ForwardRef] = {}
_DEFS_CACHE: dict[str, type[BaseModel] | ForwardRef] = {}

def _get_python_type(
    schema: dict[str, Any],
    recursion_depth: int = 0,
) -> type | ForwardRef:
    """Recursively determines the Python type hint for a given schema fragment.

    Args:
        schema: The JSON schema fragment.
        recursion_depth: Current depth of recursion.

    Returns:
        The corresponding Python type or a ForwardRef.

    Raises:
        ValueError: If a $ref cannot be resolved or schema is invalid.
        RecursionError: If recursion depth limit is exceeded.
    """
    if recursion_depth > _RECURSION_DEPTH_LIMIT:
        raise RecursionError(
            f"Maximum recursion depth ({_RECURSION_DEPTH_LIMIT}) exceeded. "
            "Check schema for circular references.",
        )

    if not isinstance(schema, dict):
         # Handle cases where schema might be improperly formatted
         logging.warning(f"Encountered non-dict schema fragment: {schema}. Returning Any.")
         return Any

    # 1. Handle $ref (references to definitions)
    if "$ref" in schema:
        ref_path = schema["$ref"]
        try:
            # Expecting format like "#/$defs/ModelName"
            def_name = ref_path.split("/")[-1]
        except (IndexError, AttributeError):
             raise ValueError(f"Invalid $ref format: {ref_path}")

        # Check caches first
        if def_name in _DEFS_CACHE:
            return _DEFS_CACHE[def_name]
        if def_name in _MODEL_CACHE: # Could be a reference to the model currently being defined
            return _MODEL_CACHE[def_name]
        # If not found, create a ForwardRef. Pydantic V2 resolves these later via model_rebuild.
        logging.info(f"Creating ForwardRef for unresolved $ref: {ref_path}")
        fwd_ref = ForwardRef(def_name)
        # Store the ForwardRef in the cache
        _MODEL_CACHE[def_name] = fwd_ref
        # If this ref points to a definition, ensure it's in the defs cache too
        # (though it will likely be populated properly when definitions are processed)
        # _DEFS_CACHE[def_name] = fwd_ref # Let definition processing handle defs cache primarily
        return fwd_ref

    # 2. Handle explicit type definitions
    schema_type = schema.get("type")
    possible_types: list[type | ForwardRef] = []

    # 2a. Handle Unions defined as "type": ["type1", "type2", ...]
    if isinstance(schema_type, list):
        for t in schema_type:
            mapped_type = TYPE_MAP.get(t)
            if mapped_type:
                possible_types.append(mapped_type)
            elif t == "object":
                possible_types.append(dict[str, Any])
            elif t == "array":
                items_schema = schema.get("items", {})
                item_type = _get_python_type(items_schema, recursion_depth + 1) if items_schema else Any
                possible_types.append(list[item_type]) # type: ignore[valid-type]
            else:
                 logging.warning(f"Unknown type '{t}' in type list: {schema_type}. Skipping.")
        if not possible_types:
             return Any

    # 2b. Handle single type string: "type": "typename"
    elif isinstance(schema_type, str):
        mapped_type = TYPE_MAP.get(schema_type)
        if mapped_type:
            possible_types.append(mapped_type)
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            item_type = _get_python_type(items_schema, recursion_depth + 1) if items_schema else Any
            possible_types.append(list[item_type]) # type: ignore[valid-type]
        elif schema_type == "object":
             if "properties" in schema:
                 logging.warning(
                     f"Inline object with properties found (not using $ref). "
                     f"Treating as Dict[str, Any]. Schema: {schema.get('title', 'N/A')}",
                 )
             possible_types.append(dict[str, Any])
        else:
             logging.warning(f"Unknown single type '{schema_type}'. Returning Any.")
             return Any

    # 2c. Handle anyOf (another way to express unions)
    elif "anyOf" in schema:
        any_of_schemas = schema["anyOf"]
        if isinstance(any_of_schemas, list):
            for sub_schema in any_of_schemas:
                 possible_types.append(_get_python_type(sub_schema, recursion_depth + 1))
        else:
             logging.warning(f"Invalid 'anyOf' format (expected list): {any_of_schemas}. Returning Any.")
             return Any

    # 2d. Handle case where 'type' key is missing
    elif schema_type is None:
        if "properties" in schema:
            logging.warning(
                 f"Schema object without explicit 'type' or '$ref'. Treating as Dict[str, Any]. "
                 f"Schema: {schema.get('title', 'N/A')}",
            )
            possible_types.append(dict[str, Any])
        elif "items" in schema: # Implied 'array' type
            items_schema = schema.get("items", {})
            item_type = _get_python_type(items_schema, recursion_depth + 1) if items_schema else Any
            possible_types.append(list[item_type]) # type: ignore[valid-type]
        else:
             return Any # Cannot determine type

    # 3. Process collected types into a final type hint (Union/Optional)
    if not possible_types:
         return Any

    has_null = type(None) in possible_types
    actual_types = tuple(t for t in possible_types if t is not type(None))

    if not actual_types:
        return type(None) # Only None/null was possible
    if len(actual_types) == 1:
        final_type = actual_types[0]
        return Optional[final_type] if has_null else final_type
    # Use Union[] for multiple types
    union_type = Union[actual_types] # type: ignore[arg-type]
    return Optional[union_type] if has_null else union_type


def _create_model_recursive(
    model_name: str,
    schema: dict[str, Any],
    recursion_depth: int = 0,
) -> type[BaseModel]:
    """Recursively creates a Pydantic V2 BaseModel from its schema definition.

    Args:
        model_name: The desired name for the Pydantic model.
        schema: The JSON schema fragment defining the model.
        recursion_depth: Current depth of recursion.

    Returns:
        The dynamically created Pydantic BaseModel class.

    Raises:
        RecursionError: If recursion depth limit is exceeded.
        RuntimeError: If Pydantic fails to create the model.
    """
    if recursion_depth > _RECURSION_DEPTH_LIMIT:
        raise RecursionError(
            f"Maximum recursion depth ({_RECURSION_DEPTH_LIMIT}) exceeded while creating model "
            f"'{model_name}'. Check schema for circular references.",
        )

    # Use cache if model already created or being created (ForwardRef)
    if model_name in _MODEL_CACHE:
        cached_val = _MODEL_CACHE[model_name]
        # If it's already a BaseModel type, return it directly
        if isinstance(cached_val, type) and issubclass(cached_val, BaseModel):
            return cached_val
        # If it's a ForwardRef, continue to create the model below
        if isinstance(cached_val, ForwardRef):
             pass # Continue processing below

    # Add a ForwardRef to cache temporarily to handle self/circular references
    if model_name not in _MODEL_CACHE:
        _MODEL_CACHE[model_name] = ForwardRef(model_name)
        # Also update _DEFS_CACHE if this name corresponds to a definition key
        if model_name in _DEFS_CACHE and isinstance(_DEFS_CACHE.get(model_name), ForwardRef):
             _DEFS_CACHE[model_name] = _MODEL_CACHE[model_name]


    fields: dict[str, tuple[type | ForwardRef, Any]] = {}
    properties = schema.get("properties", {})
    required_fields: set[str] = set(schema.get("required", []))

    # Iterate through properties defined in the schema
    for field_name, field_props in properties.items():
        if not isinstance(field_props, dict):
             logging.warning(
                 f"Field '{field_name}' in model '{model_name}' has invalid "
                 f"properties schema (expected dict): {field_props}. Skipping field.",
             )
             continue

        # Determine the type hint for the field
        try:
            field_type = _get_python_type(field_props, recursion_depth + 1)
        except RecursionError as e:
            logging.exception(
                 f"Recursion limit hit parsing type for '{model_name}.{field_name}'. Using Any. Error: {e}",
            )
            field_type = Any
        except ValueError as e:
            logging.exception(
                 f"Type resolution error for '{model_name}.{field_name}'. Using Any. Error: {e}",
            )
            field_type = Any

        # Determine if required and default value (Pydantic V2 style)
        is_required = field_name in required_fields
        default_value = field_props.get("default") # Get default from schema

        # Pydantic V2 Field definition: use Ellipsis (...) for required fields without a default
        field_definition: Any = ... # Ellipsis marks required

        if not is_required:
            # Optional field: Default is None unless overridden by schema's 'default'
            field_definition = default_value if default_value is not None else None
            # Ensure the type hint includes Optional if it's not already a Union including None
            # Check for existing Optional/Union[..., None] structure
            is_already_optional = False
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                 if type(None) in getattr(field_type, "__args__", ()):
                     is_already_optional = True
            # Check if it's exactly type(None)
            if field_type is type(None):
                 is_already_optional = True

            if not is_already_optional:
                 field_type = Optional[field_type] # type: ignore[arg-type]

        elif default_value is not None:
            # Required field *with* an explicit default value specified in the schema
            field_definition = default_value

        # Could enhance this to use pydantic.Field for more details like title, description
        # field_info = Field(
        #     default=field_definition,
        #     title=field_props.get('title'),
        #     description=field_props.get('description'),
        # )
        # fields[field_name] = (field_type, field_info)
        fields[field_name] = (field_type, field_definition)

    # Create the Pydantic V2 model using create_model
    try:
        created_model: type[BaseModel] = create_model(
             model_name,
             __base__=BaseModel, # Explicitly inherit from BaseModel
             **fields, # type: ignore[arg-type] # Pass fields dict
        )
    except Exception as e:
        logging.exception(f"Pydantic create_model failed for '{model_name}' with fields {fields}.")
        # Fallback or re-raise depending on desired robustness
        raise RuntimeError(f"Failed to create Pydantic model '{model_name}'") from e

    # --- Post-creation updates ---
    # 1. Update global namespace for ForwardRef resolution
    #    This makes the created type available by name for resolving ForwardRefs.
    globals()[model_name] = created_model

    # 2. Replace ForwardRef in caches with the actual created model type
    _MODEL_CACHE[model_name] = created_model
    if model_name in _DEFS_CACHE: # Update defs cache as well if it was a definition
         _DEFS_CACHE[model_name] = created_model

    # 3. Trigger resolution of ForwardRefs using model_rebuild (crucial for V2)
    #    This should be called after the model is defined and potentially in globals().
    try:
        # Call model_rebuild safely, handling potential errors during rebuild
        created_model.model_rebuild(force=True)
        logging.info(f"Model '{model_name}' created and rebuilt successfully.")
    except Exception as e:
        # Log error during rebuild but proceed; some refs might remain unresolved
        logging.warning(
            f"Exception during model_rebuild for '{model_name}': {e}. "
            "ForwardRefs might not be fully resolved.",
        )
        # Optionally re-raise:
        # raise RuntimeError(f"Failed to rebuild model '{model_name}' and resolve ForwardRefs.") from e

    return created_model


def create_pydantic_model_from_schema(
    schema: dict[str, Any],
    model_name: str | None = None,
) -> type[BaseModel]:
    """Creates a Pydantic V2 BaseModel class dynamically from a JSON schema dictionary.

    Handles nested models defined in the schema's '$defs' section and resolves
    ForwardRefs using Pydantic V2 mechanisms.

    Args:
        schema: The dictionary representing the JSON schema (e.g., from
                some_model.model_json_schema()).
        model_name: Optional name for the top-level model. If None, uses the
                    'title' from the schema, falling back to "DynamicModel".

    Returns:
        A dynamically created Pydantic BaseModel class corresponding to the schema.

    Raises:
        ValueError: If the schema is invalid or essential parts are missing.
        RecursionError: If the schema contains deeply nested or circular references
                       exceeding the depth limit.
        RuntimeError: If Pydantic fails to create the model.
    """
    # --- Initialization ---
    _MODEL_CACHE.clear()
    _DEFS_CACHE.clear()

    if not isinstance(schema, dict):
        raise ValueError("Invalid schema: Input must be a dictionary.")

    # Determine the name for the top-level model
    top_level_model_name = model_name or schema.get("title", "DynamicModel")

    # --- Step 1: Pre-process definitions ($defs) ---
    # Create ForwardRefs for all definitions first to handle potential
    # out-of-order references or circular dependencies within $defs.
    definitions = schema.get(_DEFS_KEY, {})
    if isinstance(definitions, dict):
        for def_name in definitions.keys():
            if def_name not in _DEFS_CACHE:
                 fwd_ref = ForwardRef(def_name)
                 _DEFS_CACHE[def_name] = fwd_ref
                 # Also add to model cache, as it might be referenced directly
                 _MODEL_CACHE[def_name] = fwd_ref

        # Now, recursively create models for all definitions. This will resolve
        # the ForwardRefs where possible and call model_rebuild internally.
        for def_name, def_schema in definitions.items():
            if not isinstance(def_schema, dict):
                logging.warning(f"Invalid schema found for definition '{def_name}'. Skipping.")
                continue
            # Check if it's still a ForwardRef (meaning not processed yet by recursion)
            if isinstance(_DEFS_CACHE.get(def_name), ForwardRef) or def_name not in _DEFS_CACHE:
                 try:
                     # This call will create/update the model in the caches
                     _create_model_recursive(def_name, def_schema, recursion_depth=0)
                 except (RecursionError, ValueError, RuntimeError) as e:
                      logging.exception(f"Error processing definition '{def_name}': {e}. Model creation might fail.")
                      # Mark as failed/unprocessed - keep ForwardRef or set to None?
                      # Keeping ForwardRef might be better if other parts succeed
                      # Or raise to halt execution:
                      # raise RuntimeError(f"Failed to process definition '{def_name}'") from e
    elif _DEFS_KEY in schema:
         logging.warning(f"'{_DEFS_KEY}' key found but is not a dictionary. Skipping definitions.")

    # --- Step 2: Create the main model ---
    # Check if the main model was already created (e.g., if schema was just a $ref)
    if top_level_model_name in _MODEL_CACHE:
        cached_model = _MODEL_CACHE[top_level_model_name]
        if isinstance(cached_model, type) and issubclass(cached_model, BaseModel):
             final_model = cached_model # Already fully created
        else:
             # It was a ForwardRef or something went wrong, try creating it properly
             logging.info(f"Top-level model '{top_level_model_name}' was a ForwardRef, creating now.")
             final_model = _create_model_recursive(top_level_model_name, schema, recursion_depth=0)
    else:
        # Create the top-level model using the main schema content
        final_model = _create_model_recursive(top_level_model_name, schema, recursion_depth=0)

    # --- Step 3: Final model rebuild (Optional but can catch stragglers) ---
    # A final rebuild on the top-level model *after* all definitions might help ensure
    # all nested ForwardRefs within its structure are fully resolved.
    try:
        final_model.model_rebuild(force=True)
        logging.info(f"Final rebuild completed for top-level model '{final_model.__name__}'.")
    except Exception as e:
        logging.warning(
            f"Final model_rebuild for '{final_model.__name__}' failed: {e}. "
            "Some ForwardRefs might remain unresolved.",
        )

    # Optional: Clean up globals()? Be careful not to remove genuinely defined models.
    # Maybe remove only names that still map to ForwardRef in _MODEL_CACHE after all rebuilds.

    return final_model


# ==============================================================================
# Example Usage (within __main__ block)
# ==============================================================================
if __name__ == "__main__":
    import json # Keep json import local to the example if only used here
    import logging # Ensure logging is configured if not already global

    # Configure logging if it wasn't set globally
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print(f"Using Pydantic Version: {pydantic.VERSION}\n")

    # --- Define original Pydantic models ---
    class Address(BaseModel):
        street_address: str
        city: str
        zip_code: Optional[str] = None

    class Person(BaseModel):
        name: str
        age: int
        is_student: bool = False
        address: Address # Nested model
        tags: list[str]
        previous_addresses: Optional[list[Address]] = None

    # --- Get the JSON schema ---
    person_schema = Person.model_json_schema()

    print("--- Original Person Schema ---")
    print(json.dumps(person_schema, indent=2))
    print("-" * 30)

    # --- Reconstruct the model from the schema ---
    print("\n--- Reconstructing Model ---")
    try:
        ReconstructedPerson = create_pydantic_model_from_schema(person_schema)
        print(f"Successfully reconstructed model: {ReconstructedPerson.__name__}")

        # --- Inspect the reconstructed model ---
        print("\n--- Reconstructed Model Fields ---")
        # Use Pydantic V2 inspection API
        for name, field_info in ReconstructedPerson.model_fields.items():
             print(f"  - {name}:")
             print(f"      Annotation: {field_info.annotation}")
             print(f"      Required:   {field_info.is_required()}")
             # Use get_default() for potentially computed defaults, otherwise .default
             default_val = field_info.get_default(call_default_factory=False)
             print(f"      Default:    {default_val!r}") # Use !r for representation

        # --- Test instantiation ---
        print("\n--- Testing Instantiation ---")
        person_data = {
            "name": "Alice",
            "age": 30,
            "address": {
                "street_address": "123 Main St",
                "city": "Anytown",
                "zip_code": "12345"
            },
            "tags": ["developer", "python"],
            "previous_addresses": [
                 {"street_address": "456 Old Ave", "city": "Oldtown"}
            ]
            # is_student will use default (False)
        }

        instance = ReconstructedPerson(**person_data)
        print("Instantiation successful!")
        print("\nInstance Data (JSON):")
        print(instance.model_dump_json(indent=2)) # Use Pydantic V2 method

        # --- Test validation ---
        print("\n--- Testing Validation (Missing Required Field) ---")
        invalid_data = {
            "name": "Bob",
            # age is missing
            "address": {
                "street_address": "789 Side St",
                "city": "Sometown"
            },
            "tags": []
        }
        try:
            ReconstructedPerson(**invalid_data)
        except pydantic.ValidationError as e:
            print("Validation failed as expected:")
            # Pydantic V2 error formatting is usually quite good
            print(e)

    except (ValueError, RuntimeError, RecursionError) as e:
        print(f"\n--- Error during Person reconstruction or testing ---")
        logging.exception("Reconstruction failed") # Log full traceback


    # --- Example with circular reference ---
    print("\n" + "="*40)
    print("--- Testing Circular Reference ---")

    # Define models with circular reference manually (Pydantic V2 style)
    # Use STRING HINTS ('Employee', 'Department') for smoother schema generation

    class Department(BaseModel):
        name: str
        manager: Optional['Employee'] = None # Use string hint
        staff: list['Employee'] = []       # Use string hint

    class Employee(BaseModel):
        name: str
        department: 'Department'         # Use string hint

    # Resolve forward references manually for the example models
    # Calling model_rebuild on both is necessary for Pydantic to link the string hints
    # The order might matter less here than with ForwardRef, but calling both is key.
    Employee.model_rebuild()
    Department.model_rebuild()


    # Get schema (e.g., from Department) - This should now work
    try:
        dept_schema = Department.model_json_schema()
        print("\n--- Original Department Schema (with circular ref) ---")
        print(json.dumps(dept_schema, indent=2))
        print("-" * 30)

        # --- Reconstruct from Circular Schema ---
        print("\n--- Reconstructing Model with Circular Reference ---")

        # Provide explicit name to avoid potential conflicts if running multiple times
        ReconstructedDept = create_pydantic_model_from_schema(
             dept_schema,
             model_name="ReconstructedDept"
        )
        print(f"Successfully reconstructed model: {ReconstructedDept.__name__}")

        # --- Inspect the circularly referenced model fields ---
        print("\n--- Reconstructed Department Fields ---")
        for name, field_info in ReconstructedDept.model_fields.items():
             print(f"  - {name}: {field_info.annotation}") # Check if resolved


        print("\n--- Testing Instantiation (Circular - Structure Check) ---")

        manager_field = ReconstructedDept.model_fields.get('manager')
        manager_type = manager_field.annotation if manager_field else 'Not Found'
        print(f"Manager type annotation: {manager_type}")

        staff_field = ReconstructedDept.model_fields.get('staff')
        staff_type = staff_field.annotation if staff_field else 'Not Found'
        print(f"Staff type annotation: {staff_type}")

        # --- Check the nested 'Employee' model from the definition cache ---
        reconstructed_employee_type = _DEFS_CACHE.get('Employee') # Name from schema $defs

        if isinstance(reconstructed_employee_type, type) and issubclass(reconstructed_employee_type, BaseModel):
            print(f"\n--- Reconstructed Employee (from Cache: {reconstructed_employee_type.__name__}) Fields ---")
            for name, field_info in reconstructed_employee_type.model_fields.items():
                 print(f"  - {name}: {field_info.annotation}")
        elif isinstance(reconstructed_employee_type, ForwardRef):
             print("\nReconstructed Employee model in cache is still a ForwardRef (resolution might have failed).")
        else:
             print(f"\nCould not retrieve reconstructed Employee model from cache (found: {reconstructed_employee_type}).")

    except (pydantic.errors.PydanticSchemaGenerationError) as schema_err:
         print(f"\n--- Error Generating Schema for Manually Defined Circular Models ---")
         logging.exception("Schema generation failed")
    except (ValueError, RuntimeError, RecursionError) as e:
        print(f"\n--- Error during circular reference reconstruction or testing ---")
        logging.exception("Circular reconstruction failed")

    # --- Example with Ebiose's Graph ---
    print("\n" + "="*40)
    print("--- Testing Ebiose's Graph ---")

    # Define models with circular reference manually (Pydantic V2 style)
    # Use STRING HINTS ('Employee', 'Department') for smoother schema generation

    # Get schema (e.g., from Department) - This should now work
    try:
        from ebiose.core.engines.graph_engine.graph import Graph
        graph_schema = Graph.model_json_schema()
        print("\n--- Original Graph Schema ---")
        print(json.dumps(graph_schema, indent=2))
        print("-" * 30)

        # --- Reconstruct from Circular Schema ---
        print("\n--- Reconstructing Model ---")

        # Provide explicit name to avoid potential conflicts if running multiple times
        ReconstructedGraph = create_pydantic_model_from_schema(
             graph_schema,
             model_name="ReconstructedGraph",
        )
        print(f"Successfully reconstructed model: {ReconstructedGraph.__name__}")

        # --- Inspect the circularly referenced model fields ---
        print("\n--- Reconstructed Graph Fields ---")
        for name, field_info in ReconstructedGraph.model_fields.items():
             print(f"  - {name}: {field_info.annotation}") # Check if resolved


        # print("\n--- Testing Instantiation ---")

        # edges_field = ReconstructedGraph.model_fields.get('edges')
        # edges_type = ReconstructedGraph.annotation if edges_field else 'Not Found'
        # print(f"Edge type annotation: {edges_type}")

        # staff_field = ReconstructedDept.model_fields.get('staff')
        # staff_type = staff_field.annotation if staff_field else 'Not Found'
        # print(f"Staff type annotation: {staff_type}")

        # # --- Check the nested 'Employee' model from the definition cache ---
        # reconstructed_employee_type = _DEFS_CACHE.get('Employee') # Name from schema $defs

        # if isinstance(reconstructed_employee_type, type) and issubclass(reconstructed_employee_type, BaseModel):
        #     print(f"\n--- Reconstructed Employee (from Cache: {reconstructed_employee_type.__name__}) Fields ---")
        #     for name, field_info in reconstructed_employee_type.model_fields.items():
        #          print(f"  - {name}: {field_info.annotation}")
        # elif isinstance(reconstructed_employee_type, ForwardRef):
        #      print("\nReconstructed Employee model in cache is still a ForwardRef (resolution might have failed).")
        # else:
        #      print(f"\nCould not retrieve reconstructed Employee model from cache (found: {reconstructed_employee_type}).")

    except (pydantic.errors.PydanticSchemaGenerationError) as schema_err:
         print(f"\n--- Error Generating Schema for Manually Defined Circular Models ---")
         logging.exception("Schema generation failed")
    except (ValueError, RuntimeError, RecursionError) as e:
        print(f"\n--- Error during circular reference reconstruction or testing ---")
        logging.exception("Circular reconstruction failed")

# if __name__ == "__main__":
#     from ebiose.core.engines.graph_engine.graph import Graph
#     json_dict = Graph.model_json_schema()

#     # Build model from JSON schema
#     model = build_model_from_json(json_dict)
#     print(model.model_json_schema(indent=2))

#     # Build recursive model
#     recursive_model = build_recursive(json_dict)
#     print(recursive_model.model_json_schema(indent=2))
