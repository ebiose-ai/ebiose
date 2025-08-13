import pytest
from pydantic import BaseModel
from ebiose.core.agent_engine import AgentEngine, AgentEngineRunError

class ConcreteAgentEngine(AgentEngine):
    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        if hasattr(agent_input, "error") and agent_input.error:
            raise ValueError("Test error")
        return "success"

@pytest.fixture
def agent_engine():
    return ConcreteAgentEngine(engine_type="concrete", agent_id="test_agent")

@pytest.mark.asyncio
async def test_agent_engine_run_success(agent_engine):
    class InputModel(BaseModel):
        data: str

    input_data = InputModel(data="test")
    result = await agent_engine.run(input_data, "master_id", "cycle_id")
    assert result == "success"

@pytest.mark.asyncio
async def test_agent_engine_run_error(agent_engine):
    class InputModel(BaseModel):
        error: bool

    input_data = InputModel(error=True)
    with pytest.raises(AgentEngineRunError) as excinfo:
        await agent_engine.run(input_data, "master_id", "cycle_id")

    assert "Error during agent engine run" in str(excinfo.value)
    assert "Test error" in str(excinfo.value)
    assert "Agent: test_agent" in str(excinfo.value)

def test_agent_engine_run_error_str():
    error = AgentEngineRunError("test message")
    assert str(error) == "AgentRunError: test message"

def test_agent_engine_run_error_str_with_agent_id():
    error = AgentEngineRunError("test message", agent_identifier="agent123")
    assert str(error) == "AgentRunError (Agent: agent123): test message"

def test_agent_engine_run_error_str_with_original_exception():
    try:
        raise ValueError("original error")
    except ValueError as e:
        error = AgentEngineRunError("test message", original_exception=e)
        assert "test message" in str(error)
        assert "ValueError: original error" in str(error)
