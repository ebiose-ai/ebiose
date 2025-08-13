import pytest
from unittest.mock import patch, MagicMock
import datetime
from uuid import uuid4

from ebiose.core.events import (
    BaseEvent,
    ForgeCycleStartedEvent,
    elastic_sink,
    init_logger,
)

@patch("ebiose.core.events.EbioseAPIClient.log")
def test_elastic_sink(mock_log):
    record = {
        "extra": {
            "event_payload": {"event": "test"},
            "other_data": "some_value"
        },
        "time": datetime.datetime.now(),
        "level": MagicMock(name="INFO"),
        "message": "test message",
        "file": MagicMock(name="test_file.py"),
        "line": 123,
        "function": "test_function"
    }

    # Create a mock message object
    message = MagicMock()
    message.record = record

    elastic_sink(message)

    mock_log.assert_called_once()
    args, kwargs = mock_log.call_args
    assert "event" in kwargs["message"]
    assert "loguru" in kwargs["message"]

@patch("ebiose.core.events.event_logger")
def test_init_logger(mock_logger):
    user_id = "user1"
    forge_id = uuid4()
    forge_cycle_id = uuid4()

    init_logger(user_id, forge_id, forge_cycle_id)

    mock_logger.bind.assert_called_once_with(
        user_id=user_id,
        forge_id=forge_id,
        forge_cycle_id=forge_cycle_id,
    )

def test_base_event():
    event = BaseEvent()
    assert event.event_name == "BaseEvent"
    assert "timestamp" in event.to_dict()

@patch("ebiose.core.events.event_logger")
def test_base_event_log(mock_logger):
    event = ForgeCycleStartedEvent(
        forge_name="test_forge",
        forge_description="a test forge",
        config={}
    )
    event.log()

    mock_logger.bind.assert_called_once()
    mock_logger.bind.return_value.info.assert_called_once()
