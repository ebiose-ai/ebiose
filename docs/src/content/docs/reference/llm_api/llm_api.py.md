---
title: llm_api.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/llm_api/llm_api.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `llm_api.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 



---

## <kbd>class</kbd> `LLMAPIConfig`





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

## <kbd>class</kbd> `LLMApi`







---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agent_cost`

```python
add_agent_cost(agent_id: 'str', cost: 'float') → None
```

Add the cost for a specific agent. 

---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_agent_cost`

```python
get_agent_cost(agent_id: 'str') → float
```

Get the cost spent on a specific agent. 

---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_agents_total_cost`

```python
get_agents_total_cost() → float
```

Get the total cost spent on each agent. 

---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_total_cost`

```python
get_total_cost() → float
```

Get the total cost spent on the agents. 

---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `initialize`

```python
initialize(
    mode: "Literal['local', 'cloud']",
    lite_llm_api_key: 'str | None' = None,
    llm_api_config: 'LLMAPIConfig | None' = None
) → LLMApi
```





---

<a href="../../../../../../ebiose/llm_api/llm_api.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `update_total_cost`

```python
update_total_cost(new_cost: 'float | None' = None) → None
```

Update the total cost and the cost for a specific agent. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
