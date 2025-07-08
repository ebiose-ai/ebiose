---
title: client.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/cloud_client/client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `client.py`






---

## <kbd>class</kbd> `AgentEngineInputModel`
Input model for agent engine configuration. 


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

## <kbd>class</kbd> `AgentEngineOutputModel`
Output model for agent engine configuration. 


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

## <kbd>class</kbd> `AgentInputModel`
Input model for creating or updating an agent. 


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

## <kbd>class</kbd> `AgentOutputModel`
Output model representing an agent. 


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

## <kbd>class</kbd> `AgentType`
Enum for Agent Types. 





---

## <kbd>class</kbd> `ApiKeyInputModel`
Input model for creating or updating an API key. 


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

## <kbd>class</kbd> `ApiKeyOutputModel`
Output model representing an API key. 


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

## <kbd>class</kbd> `EbioseAPIClient`
Facade client providing a high-level interface to the EbioseCloud API. 




---

<a href="../../../../../../ebiose/cloud_client/client.py#L518"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agent_during_cycle`

```python
add_agent_during_cycle(
    forge_cycle_uuid: 'str',
    agent_data: 'AgentInputModel'
) → AgentOutputModel
```

Adds a single agent during an active forge cycle. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L523"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_agents_during_cycle`

```python
add_agents_during_cycle(
    forge_cycle_uuid: 'str',
    agents_data: 'list[AgentInputModel]'
) → None
```

Adds multiple agents during an active forge cycle. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L469"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_new_api_key`

```python
add_new_api_key(data: 'ApiKeyInputModel') → bool
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L478"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `add_new_forge`

```python
add_new_forge(data: 'ForgeInputModel') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L494"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `begin_new_forge_cycle`

```python
begin_new_forge_cycle(
    forge_uuid: 'str',
    data: 'ForgeCycleInputModel',
    override_key: 'bool | None' = None
) → NewCycleOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L498"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `conclude_forge_cycle`

```python
conclude_forge_cycle(
    forge_cycle_uuid: 'str',
    agents_data: 'list[AgentInputModel]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L502"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_forge_cycle_spend`

```python
get_forge_cycle_spend(forge_cycle_uuid: 'str') → float
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L482"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_specific_forge`

```python
get_specific_forge(forge_uuid: 'str') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L474"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `list_all_forges`

```python
list_all_forges() → list[ForgeOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L506"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `log_forge_cycle_usage`

```python
log_forge_cycle_usage(forge_cycle_uuid: 'str', cost: 'float') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L529"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `log_message`

```python
log_message(data: 'LogEntryInputModel') → LogEntryOutputModel
```

Sends a log entry to the logging service. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L514"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `make_deduct_compute_banks_for_forge_cycle`

```python
make_deduct_compute_banks_for_forge_cycle(
    forge_cycle_uuid: 'str',
    deductions: 'dict[str, float]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L486"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `modify_forge`

```python
modify_forge(forge_uuid: 'str', data: 'ForgeInputModel') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L510"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `pick_agents_for_forge_cycle`

```python
pick_agents_for_forge_cycle(
    forge_cycle_uuid: 'str',
    nb_agents: 'int'
) → list[AgentOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L490"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `remove_forge`

```python
remove_forge(forge_uuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L440"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `set_client_credentials`

```python
set_client_credentials(
    base_url: 'str',
    api_key: 'str | None' = None,
    bearer_token: 'str | None' = None
) → None
```

Sets the API client credentials. 


---

## <kbd>class</kbd> `EbioseCloudAuthError`
Exception for authentication-related errors. 

<a href="../../../../../../ebiose/cloud_client/client.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    message,
    status_code: 'int | None' = None,
    response_text: 'str | None' = None
)
```









---

## <kbd>class</kbd> `EbioseCloudClient`
Core client for interacting with the EbioseCloud API. 

<a href="../../../../../../ebiose/cloud_client/client.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    base_url: 'str',
    api_key: 'str | None' = None,
    bearer_token: 'str | None' = None,
    timeout: 'int' = 30
)
```

Initializes the EbioseCloudClient. 



**Args:**
 
 - <b>`base_url`</b>:  The base URL for the API. 
 - <b>`api_key`</b>:  The API key for 'ApiKey' authentication. 
 - <b>`bearer_token`</b>:  The Bearer token for 'Bearer' authentication. 
 - <b>`timeout`</b>:  Request timeout in seconds. 




---

<a href="../../../../../../ebiose/cloud_client/client.py#L402"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_agent_during_forge_cycle`

```python
add_agent_during_forge_cycle(
    forge_cycle_uuid: 'str',
    data: 'AgentInputModel'
) → AgentOutputModel
```

New: Corresponds to POST /forges/cycles/{forgeCycleUuid}/agent. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L406"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_agents_during_forge_cycle`

```python
add_agents_during_forge_cycle(
    forge_cycle_uuid: 'str',
    agents_data: 'list[AgentInputModel]'
) → None
```

New: Corresponds to POST /forges/cycles/{forgeCycleUuid}/agents. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L349"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_agents_to_ecosystem`

```python
add_agents_to_ecosystem(
    ecosystem_uuid: 'str',
    agents_data: 'list[AgentInputModel]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L287"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_api_key`

```python
add_api_key(data: 'ApiKeyInputModel') → bool
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L371"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_forge`

```python
add_forge(data: 'ForgeInputModel') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L411"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_log_entry`

```python
add_log_entry(data: 'LogEntryInputModel') → LogEntryOutputModel
```

Corresponds to POST /logging. 

---

<a href="../../../../../../ebiose/cloud_client/client.py#L364"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_single_agent_to_ecosystem`

```python
add_single_agent_to_ecosystem(
    ecosystem_uuid: 'str',
    agent_data: 'AgentInputModel'
) → AgentOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L334"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `create_ecosystem`

```python
create_ecosystem(data: 'EcosystemInputModel') → EcosystemOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L416"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `create_user`

```python
create_user(data: 'UserInputModel') → UserOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L396"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `deduct_compute_banks_for_forge_cycle`

```python
deduct_compute_banks_for_forge_cycle(
    forge_cycle_uuid: 'str',
    deductions: 'dict[str, float]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L355"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete_agents_from_ecosystem`

```python
delete_agents_from_ecosystem(
    ecosystem_uuid: 'str',
    agent_uuids: 'list[str]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L302"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete_api_key`

```python
delete_api_key(apiKeyUuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L346"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete_ecosystem`

```python
delete_ecosystem(uuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L380"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete_forge`

```python
delete_forge(forge_uuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L428"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete_user`

```python
delete_user(userUuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L387"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `end_forge_cycle`

```python
end_forge_cycle(
    forge_cycle_uuid: 'str',
    agents_data: 'list[AgentInputModel]'
) → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L358"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_agent_in_ecosystem`

```python
get_agent_in_ecosystem(
    ecosystem_uuid: 'str',
    agent_uuid: 'str'
) → AgentOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L299"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_api_key`

```python
get_api_key(apiKeyUuid: 'str') → ApiKeyOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L290"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_api_keys`

```python
get_api_keys() → list[ApiKeyOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_ecosystem`

```python
get_ecosystem(uuid: 'str') → EcosystemOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L374"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_forge`

```python
get_forge(forge_uuid: 'str') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L368"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_forges`

```python
get_forges() → list[ForgeOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L390"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_spend`

```python
get_spend(forge_cycle_uuid: 'str') → float
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L422"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_user`

```python
get_user(userUuid: 'str') → UserOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L431"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_user_by_email`

```python
get_user_by_email(email: 'str') → UserOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L352"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `list_agents_in_ecosystem`

```python
list_agents_in_ecosystem(ecosystem_uuid: 'str') → list[AgentOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L337"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `list_ecosystems`

```python
list_ecosystems() → list[EcosystemOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L419"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `list_users`

```python
list_users() → list[UserOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L312"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `login`

```python
login(email: 'str', password: 'str') → LoginOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L315"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `login_github`

```python
login_github(code: 'str') → LoginOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L399"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `record_forge_cycle_usage`

```python
record_forge_cycle_usage(forge_cycle_uuid: 'str', cost: 'float') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L327"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `refresh_token`

```python
refresh_token(token: 'str') → str
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `select_agents_for_forge_cycle`

```python
select_agents_for_forge_cycle(
    forge_cycle_uuid: 'str',
    nb_agents: 'int'
) → list[AgentOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L293"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `self_add_api_key`

```python
self_add_api_key(data: 'SelfApiKeyInputModel') → bool
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L308"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `self_delete_api_key`

```python
self_delete_api_key(apiKeyUuid: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L296"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `self_get_api_keys`

```python
self_get_api_keys() → list[ApiKeyOutputModel]
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L321"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `self_update`

```python
self_update(data: 'SelfUserInputModel') → UserOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L318"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `sign_up`

```python
sign_up(data: 'SignupInputModel') → UserOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L383"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `start_new_forge_cycle`

```python
start_new_forge_cycle(
    forge_uuid: 'str',
    data: 'ForgeCycleInputModel',
    override_key: 'bool | None' = None
) → NewCycleOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_agent_in_ecosystem`

```python
update_agent_in_ecosystem(
    ecosystem_uuid: 'str',
    agent_uuid: 'str',
    agent_data: 'AgentInputModel'
) → AgentOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L305"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_api_key`

```python
update_api_key(apiKeyUuid: 'str', data: 'ApiKeyInputModel') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L343"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_ecosystem`

```python
update_ecosystem(
    uuid: 'str',
    data: 'EcosystemInputModel'
) → EcosystemOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L377"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_forge`

```python
update_forge(forge_uuid: 'str', data: 'ForgeInputModel') → ForgeOutputModel
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L324"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_password`

```python
update_password(new_password: 'str') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L425"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_user`

```python
update_user(userUuid: 'str', data: 'UserInputModel') → None
```





---

<a href="../../../../../../ebiose/cloud_client/client.py#L330"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `user_info`

```python
user_info() → UserOutputModel
```






---

## <kbd>class</kbd> `EbioseCloudError`
Base exception for EbioseCloud API errors. 

<a href="../../../../../../ebiose/cloud_client/client.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    message,
    status_code: 'int | None' = None,
    response_text: 'str | None' = None
)
```









---

## <kbd>class</kbd> `EbioseCloudHTTPError`
Exception for HTTP errors (4xx, 5xx). 

<a href="../../../../../../ebiose/cloud_client/client.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    message,
    status_code: 'int | None' = None,
    response_text: 'str | None' = None
)
```









---

## <kbd>class</kbd> `EcosystemInputModel`
Input model for creating or updating an ecosystem. 


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

## <kbd>class</kbd> `EcosystemOutputModel`
Output model representing an ecosystem. 


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

## <kbd>class</kbd> `ForgeCycleInputModel`
Input model for starting a new forge cycle. 


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

## <kbd>class</kbd> `ForgeCycleOutputModel`
Output model representing a forge cycle's state. Updated structure. 


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

## <kbd>class</kbd> `ForgeInputModel`
Input model for creating or updating a forge. 


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

## <kbd>class</kbd> `ForgeOutputModel`
Output model representing a forge. 


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

## <kbd>class</kbd> `LogEntryInputModel`
Input model for creating a new log entry. 


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

## <kbd>class</kbd> `LogEntryOutputModel`
Output model for a log entry response. 


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

## <kbd>class</kbd> `LoginOutputModel`
Output model for a successful login. 


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

## <kbd>class</kbd> `NewCycleOutputModel`
Output model after starting a new forge cycle. 


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

## <kbd>class</kbd> `Role`
Enum for User Roles. 





---

## <kbd>class</kbd> `SelfApiKeyInputModel`
Input model for creating a new API key for the current user. 


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

## <kbd>class</kbd> `SelfUserInputModel`
Input model for the current user updating their own profile. 


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

## <kbd>class</kbd> `SignupInputModel`
Input model for new user registration. 


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

## <kbd>class</kbd> `UserInputModel`
Input model for creating or updating a user (admin operation). 


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

## <kbd>class</kbd> `UserOutputModel`
Output model representing a user's data. 


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

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
