import pytest
from pydantic import BaseModel
from ebiose.tools.json_schema_to_pydantic import create_pydantic_model_from_schema

def test_simple_schema():
    schema = {
        "title": "Simple",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
    model = create_pydantic_model_from_schema(schema)
    assert model.__name__ == "Simple"
    instance = model(name="test", age=10)
    assert instance.name == "test"
    assert instance.age == 10

def test_nested_schema():
    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"$ref": "#/$defs/Address"},
        },
        "$defs": {
            "Address": {
                "title": "Address",
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                },
            }
        },
    }
    model = create_pydantic_model_from_schema(schema)
    instance = model(name="test", address={"street": "main st"})
    assert instance.address.street == "main st"

def test_list_of_objects():
    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "addresses": {
                "type": "array",
                "items": {"$ref": "#/$defs/Address"},
            },
        },
        "$defs": {
            "Address": {
                "title": "Address",
                "type": "object",
                "properties": {"street": {"type": "string"}},
            }
        },
    }
    model = create_pydantic_model_from_schema(schema)
    instance = model(addresses=[{"street": "main st"}])
    assert len(instance.addresses) == 1
    assert instance.addresses[0].street == "main st"

def test_union_and_optional():
    schema = {
        "title": "UnionOptional",
        "type": "object",
        "properties": {
            "value": {"type": ["string", "integer"]},
            "optional_value": {"type": ["string", "null"]},
        },
    }
    model = create_pydantic_model_from_schema(schema)
    instance1 = model(value="test")
    assert instance1.value == "test"
    instance2 = model(value=123)
    assert instance2.value == 123

def test_circular_reference():
    schema = {
        "title": "Employee",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "manager": {"$ref": "#/$defs/Employee"},
        },
        "$defs": {
            "Employee": {
                "title": "Employee",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "manager": {"$ref": "#/$defs/Employee"},
                },
            }
        },
    }
    model = create_pydantic_model_from_schema(schema)
    instance = model(name="boss", manager=None)
    assert instance.name == "boss"

from typing import Union

def test_anyof_schema():
    schema = {
        "title": "AnyOfTest",
        "anyOf": [
            {"type": "string"},
            {"type": "integer"},
        ],
    }
    model = create_pydantic_model_from_schema(schema, model_name="AnyOfWrapper")
    assert model is not None

def test_missing_type():
    schema = {
        "title": "MissingType",
        "properties": {
            "value": {},
        },
    }
    model = create_pydantic_model_from_schema(schema)
    assert "value" in model.model_fields

def test_default_value():
    schema = {
        "title": "DefaultValue",
        "type": "object",
        "properties": {
            "name": {"type": "string", "default": "test"},
        },
    }
    model = create_pydantic_model_from_schema(schema)
    instance = model()
    assert instance.name == "test"

def test_invalid_ref(caplog):
    schema = {
        "title": "InvalidRef",
        "type": "object",
        "properties": {
            "address": {"$ref": "invalid_ref"},
        },
    }
    create_pydantic_model_from_schema(schema)
    assert "Exception during model_rebuild" in caplog.text

def test_invalid_schema():
    with pytest.raises(ValueError):
        create_pydantic_model_from_schema("not a schema")
