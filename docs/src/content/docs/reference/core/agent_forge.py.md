---
title: agent_forge.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/agent_forge.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `agent_forge.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 

**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `AgentForge`





---

#### <kbd>property</kbd> description_embedding





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

<a href="../../../../../../ebiose/core/agent_forge.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `compute_fitness`

```python
compute_fitness(agent: 'Agent', **kwargs: 'dict[str, any]') → tuple[str, float]
```





---

<a href="../../../../../../ebiose/core/agent_forge.py#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `display_results`

```python
display_results(
    agents: 'dict[str, Agent]',
    agents_fitness: 'dict[str, float]'
) → None
```





---

<a href="../../../../../../ebiose/core/agent_forge.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_new_cycle`

```python
run_new_cycle(
    config: 'ForgeCycleConfig',
    ecosystem: 'Ecosystem | None' = None
) → list[Agent]
```





---

<a href="../../../../../../ebiose/core/agent_forge.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `validate_default_model_endpoint_id`

```python
validate_default_model_endpoint_id(value: 'str | None') → str
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
