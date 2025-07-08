---
title: json_schema_to_pydantic.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/tools/json_schema_to_pydantic.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `json_schema_to_pydantic.py`




**Global Variables**
---------------
- **TYPE_MAP**

---

<a href="../../../../../../ebiose/tools/json_schema_to_pydantic.py#L311"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_pydantic_model_from_schema`

```python
create_pydantic_model_from_schema(
    schema: dict[str, Any],
    model_name: str | None = None
) → type[BaseModel]
```

Creates a Pydantic V2 BaseModel class dynamically from a JSON schema dictionary. 

Handles nested models defined in the schema's '$defs' section and resolves ForwardRefs using Pydantic V2 mechanisms. 



**Args:**
 
 - <b>`schema`</b>:  The dictionary representing the JSON schema (e.g., from  some_model.model_json_schema()). 
 - <b>`model_name`</b>:  Optional name for the top-level model. If None, uses the  'title' from the schema, falling back to "DynamicModel". 



**Returns:**
 A dynamically created Pydantic BaseModel class corresponding to the schema. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the schema is invalid or essential parts are missing. 
 - <b>`RecursionError`</b>:  If the schema contains deeply nested or circular references  exceeding the depth limit. 
 - <b>`RuntimeError`</b>:  If Pydantic fails to create the model. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
