---
title: ebiose_api_client.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `ebiose_api_client.py`




**Global Variables**
---------------
- **TYPE_CHECKING**
- **ES_INDEX**

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `build_agent_input_model`

```python
build_agent_input_model(agent: 'Agent', forge_cycle_id: str) → AgentInputModel
```

Format the agent for the API. 


---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_sample_agent`

```python
get_sample_agent() → Agent
```






---

## <kbd>class</kbd> `EbioseAPIClient`







---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agent_from_forge_cycle`

```python
add_agent_from_forge_cycle(forge_cycle_id: str, agent: 'Agent') → None
```

Post a single agent in a forge cycle. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L200"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agents_from_forge_cycle`

```python
add_agents_from_forge_cycle(forge_cycle_id: str, agents: list['Agent']) → None
```

Post agents in a forge cycle. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agents_to_ecosystem`

```python
add_agents_to_ecosystem(agents: list['Agent'], ecosystem_id: str) → list[str]
```

Post agents in an ecosystem. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L267"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_forge`

```python
add_forge(name: str, description: str, ecosystem_id: str) → str | None
```





---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `delete_agents`

```python
delete_agents(ecosystem_id: str, agent_ids: list[str]) → None
```

Delete agents in an ecosystem. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L345"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `end_forge_cycle`

```python
end_forge_cycle(forge_cycle_uuid: str, winning_agents: list['Agent']) → None
```

End a forge cycle. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_agents`

```python
get_agents(ecosystem_id: str, return_ids_only: bool) → list['Agent'] | None
```





---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_cost`

```python
get_cost(forge_cycle_uuid: str) → float
```





---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_ecosystem`

```python
get_ecosystem(ecosystem_id: str) → Ecosystem | None
```

Get an ecosystem by its UUID. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_ecosystems`

```python
get_ecosystems() → list | None
```

Get all ecosystem UUIDs. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L162"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_first_ecosystem_uuid`

```python
get_first_ecosystem_uuid() → str
```

Get the first ecosystem UUID. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_user_id`

```python
get_user_id() → str | None
```

Get the user ID from the API. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `log`

```python
log(message: dict[str, any]) → None
```

Log a message to the API. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L322"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `select_agents`

```python
select_agents(
    ecosystem_id: str,
    nb_agents: int,
    forge_cycle_uuid: str
) → list['Agent']
```

Select agents from an ecosystem. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `set_client`

```python
set_client() → None
```

Set the API client with the provided API key. 

---

<a href="../../../../../../ebiose/cloud_client/ebiose_api_client.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `start_new_forge_cycle`

```python
start_new_forge_cycle(
    ecosystem_id: str,
    forge_name: str,
    forge_description: str,
    forge_cycle_config: 'CloudForgeCycleConfig',
    override_key: bool | None = None
) → tuple[str, str, str, str]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
