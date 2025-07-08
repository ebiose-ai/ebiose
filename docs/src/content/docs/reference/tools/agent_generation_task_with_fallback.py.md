---
title: agent_generation_task_with_fallback.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/tools/agent_generation_task_with_fallback.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `agent_generation_task_with_fallback.py`
Copyright (c) 2024, Inria. 

Pre-release Version - DO NOT DISTRIBUTE This software is licensed under the MIT License. See LICENSE for details. 

**Global Variables**
---------------
- **TYPE_CHECKING**

---

<a href="../../../../../../ebiose/tools/agent_generation_task_with_fallback.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `architect_agent_task`

```python
architect_agent_task(
    forge: 'AgentForge',
    architect_agent: 'Agent',
    architect_agent_input: 'BaseModel',
    genetic_operator_agent: 'Agent',
    forge_cycle_id: 'str | None' = None
) → Agent | None
```






---

<a href="../../../../../../ebiose/tools/agent_generation_task_with_fallback.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `crossover_agent_task`

```python
crossover_agent_task(
    forge: 'AgentForge',
    genetic_operator_agent: 'Agent',
    crossover_agent_input: 'BaseModel',
    architect_agent: 'Agent | None',
    parent1: 'Agent',
    parent2: 'Agent | None',
    master_agent_id: 'str | None' = None,
    forge_cycle_id: 'str | None' = None
) → Agent | None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
