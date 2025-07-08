---
title: events.py
---
<!-- markdownlint-disable -->

<a href="../../../../../../ebiose/core/events.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `events.py`




**Global Variables**
---------------
- **TYPE_CHECKING**

---

<a href="../../../../../../ebiose/core/events.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `elastic_sink`

```python
elastic_sink(message) → None
```






---

<a href="../../../../../../ebiose/core/events.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `init_logger`

```python
init_logger(
    user_id: 'str | None',
    forge_id: 'str | UUID | None',
    forge_cycle_id: 'str | UUID'
) → None
```






---

## <kbd>class</kbd> `AgentAddedToPopulationEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `AgentEvaluationCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `AgentSelectionCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `AgentSelectionStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `ArchitectAgentTaskCreatedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `BaseEvent`
Base class for all events in the system. 


---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `CrossoverAndMutationCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `CrossoverAndMutationStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `ForgeCycleEndedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `ForgeCycleFailedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `ForgeCycleStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `GenerationRunCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `GenerationRunStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `OffspringCreatedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `PopulationEvaluationCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `PopulationEvaluationStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `PopulationInitializationCompletedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```






---

## <kbd>class</kbd> `PopulationInitializationStartedEvent`





---

#### <kbd>property</kbd> event_name





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

<a href="../../../../../../ebiose/core/events.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message_override: 'str | None' = None) → None
```

Logs this event using Loguru. 

The event data is bound to the log record for consumption by structured logging sinks. 

---

<a href="../../../../../../ebiose/core/events.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_dict`

```python
to_dict() → dict[str, Any]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
