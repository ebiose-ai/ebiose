---
title: llm_api.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `llm_api.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 

**Global Variables**
---------------
- **UTC**
- **TYPE_CHECKING**


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

## <kbd>class</kbd> `LangGraphLLMApi`







---

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agent_cost`

```python
add_agent_cost(agent_id: 'str', cost: 'float') → None
```

Add the cost for a specific agent. 

---

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_agent_cost`

```python
get_agent_cost(agent_id: 'str') → float
```

Get the cost spent on a specific agent. 

---

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_agents_total_cost`

```python
get_agents_total_cost() → float
```

Get the total cost spent on each agent. 

---

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_total_cost`

```python
get_total_cost(forge_cycle_id: 'str') → float
```

Get the total cost spent on the agents. 

---

<a href="../../../../../../ebi.ose/backends/langgraph/llm_api.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `initialize`

```python
initialize(
    mode: "Literal['local', 'cloud']",
    lite_llm_api_key: 'str | None' = None,
    lite_llm_api_base: 'str | None' = None,
    llm_api_config: 'LLMAPIConfig | None' = None
) → LangGraphLLMApi
```





---

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L282"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `process_llm_call`

```python
process_llm_call(
    model_endpoint_id: 'str',
    messages: 'list[AnyMessage]',
    agent_id: 'str',
    temperature: 'float' = 0.0,
    max_tokens: 'int' = 4096,
    tools: 'list | None' = None
) → AnyMessage
```






---

## <kbd>class</kbd> `LangGraphLLMApiError`
Custom exception for errors during LLM calls. 

<a href="../../../../../../ebiose/backends/langgraph/llm_api.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    message: 'str',
    original_exception: 'Exception | None' = None,
    llm_identifier: 'str | None' = None
) → None
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
