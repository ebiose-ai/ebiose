---
title: agent_factory.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/agent_factory.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `agent_factory.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 

**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `AgentFactory`







---

<a href="../../../../../../ebiose/core/agent_factory.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `crossover_agents`

```python
crossover_agents(
    crossover_agent: 'Agent',
    input_data: 'BaseModel',
    generated_agent_engine_type: 'str | None' = None,
    generated_agent_input: 'type[BaseModel] | None' = None,
    generated_agent_output: 'type[BaseModel] | None' = None,
    generated_model_endpoint_id: 'str | None' = None,
    architect_agent: 'Agent | None' = None,
    parent_ids: 'list[str] | None' = None,
    master_agent_id: 'str | None' = None,
    forge_cycle_id: 'str | None' = None,
    forge_description: 'str | None' = None
) → tuple['Agent', 'Agent'] | 'Agent'
```





---

<a href="../../../../../../ebiose/core/agent_factory.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_agent`

```python
generate_agent(
    architect_agent: 'Agent',
    agent_input: 'dict',
    genetic_operator_agent: 'Agent | None' = None,
    generated_agent_engine_type: 'str | None' = None,
    generated_agent_input: 'type[BaseModel] | None' = None,
    generated_agent_output: 'type[BaseModel] | None' = None,
    generated_model_endpoint_id: 'str | None' = None,
    forge_cycle_id: 'str | None' = None,
    forge_description: 'str | None' = None
) → 'Agent'
```





---

<a href="../../../../../../ebiose/core/agent_factory.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_agent`

```python
load_agent(
    agent_config: 'dict',
    model_endpoint_id: 'str | None' = None
) → 'Agent'
```





---

<a href="../../../../../../ebiose/core/agent_factory.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_agent_from_api`

```python
load_agent_from_api(
    response_dict: 'AgentOutputModel',
    model_endpoint_id: 'str | None' = None
) → 'Agent'
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
