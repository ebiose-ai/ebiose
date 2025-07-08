---
title: ecosystem.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/ecosystem.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `ecosystem.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 

**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `Ecosystem`





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

<a href="../../../../../../ebiose/core/ecosystem.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_forge`

```python
add_forge(forge: 'AgentForge') → None
```





---

<a href="../../../../../../ebiose/core/ecosystem.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_agent`

```python
get_agent(agent_id: 'str') → 'Agent' | None
```





---

<a href="../../../../../../ebiose/core/ecosystem.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `new`

```python
new(initial_agents: "list['Agent'] | None" = None) → Ecosystem
```





---

<a href="../../../../../../ebiose/core/ecosystem.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `select_agents_for_forge`

```python
select_agents_for_forge(forge: 'AgentForge', n_agents: 'int') → list['Agent']
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
