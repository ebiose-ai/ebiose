"""Agent engine factory with improved architecture."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ebiose.core.models.agent_models import AgentEngine
from ebiose.core.models.exceptions import AgentEngineError

if TYPE_CHECKING:
    pass


class EngineRegistry:
    """Registry for engine types."""

    _engines: dict[str, type[AgentEngine]] = {}

    @classmethod
    def register(cls, engine_type: str, engine_class: type[AgentEngine]) -> None:
        """Register an engine type."""
        cls._engines[engine_type] = engine_class

    @classmethod
    def get_engine_class(cls, engine_type: str) -> type[AgentEngine]:
        """Get engine class by type."""
        if engine_type not in cls._engines:
            msg = f"Unknown engine type: {engine_type}"
            raise ValueError(msg)
        return cls._engines[engine_type]

    @classmethod
    def list_engine_types(cls) -> list[str]:
        """List available engine types."""
        return list(cls._engines.keys())


class AgentEngineFactory:
    """Factory for creating agent engines."""

    @staticmethod
    def create_engine(
        engine_type: str,
        agent_id: str,
        configuration: dict[str, Any],
        model_endpoint_id: str | None = None,
    ) -> AgentEngine:
        """Create an agent engine.

        Args:
            engine_type: Type of engine to create
            agent_id: ID of the agent
            configuration: Engine configuration
            model_endpoint_id: Model endpoint ID

        Returns:
            Created agent engine

        Raises:
            ValueError: If engine type is unknown
        """
        try:
            if engine_type == "langgraph_engine":
                from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine
                from ebiose.core.model_endpoint import ModelEndpoints

                if model_endpoint_id is None:
                    model_endpoint_id = ModelEndpoints.get_default_model_endpoint_id()
                
                return LangGraphEngine(
                    agent_id=agent_id,
                    configuration=configuration,
                    model_endpoint_id=model_endpoint_id,
                )
            
            # Use registry for other engines
            engine_class = EngineRegistry.get_engine_class(engine_type)
            return engine_class(
                engine_type=engine_type,
                agent_id=agent_id,
                configuration=configuration,
                model_endpoint_id=model_endpoint_id,
            )
        
        except Exception as e:
            msg = f"Failed to create engine of type '{engine_type}': {e}"
            raise AgentEngineError(msg) from e
