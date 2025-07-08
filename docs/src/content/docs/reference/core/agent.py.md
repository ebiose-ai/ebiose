---
title: agent.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/agent.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `agent.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 



---

## <kbd>class</kbd> `Agent`





---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 



---

<a href="../../../../../../ebiose/core/agent.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_embeddings`

```python
generate_embeddings() → Self
```





---

<a href="../../../../../../.venv/lib/python3.12/site-packages/langfuse/decorators/langfuse_decorator.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run`

```python
run(
    input_data: 'BaseModel',
    master_agent_id: 'str',
    forge_cycle_id: 'str | None' = None,
    **kwargs: 'dict[str, any]'
) → any
```





---

<a href="../../../../../../ebiose/core/agent.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `serialize_agent_engine`

```python
serialize_agent_engine(agent_engine: 'AgentEngine | None') → dict
```





---

<a href="../../../../../../ebiose/core/agent.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_io_models`

```python
update_io_models(
    agent_input_model: 'type[BaseModel] | None' = None,
    agent_output_model: 'type[BaseModel] | None' = None
) → None
```





---

<a href="../../../../../../ebiose/core/agent.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `validate_agent`

```python
validate_agent(data: 'any') → any
```





---

<a href="../../../../../../ebiose/core/agent.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `validate_agent_engine`

```python
validate_agent_engine(agent_engine: 'dict | AgentEngine') → AgentEngine
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
