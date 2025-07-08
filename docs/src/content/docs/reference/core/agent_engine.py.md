---
title: agent_engine.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/agent_engine.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `agent_engine.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 



---

## <kbd>class</kbd> `AgentEngine`





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

<a href="../../../../../../ebiose/core/agent_engine.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run`

```python
run(
    agent_input: 'BaseModel',
    master_agent_id: 'str',
    forge_cycle_id: 'str | None' = None,
    **kwargs: 'dict[str, any]'
) → any
```






---

## <kbd>class</kbd> `AgentEngineRunError`
Custom exception for errors during agent run. 

<a href="../../../../../../ebiose/core/agent_engine.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    message: 'str',
    original_exception: 'Exception | None' = None,
    agent_identifier: 'str | None' = None
) → None
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
