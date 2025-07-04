"""High-level facade for the Ebiose Cloud API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from ebiose.core.models.api_models import (
    AgentInputModel,
    AgentOutputModel,
    ApiKeyInputModel,
    ForgeCycleInputModel,
    ForgeInputModel,
    ForgeOutputModel,
    LogEntryInputModel,
    LogEntryOutputModel,
    NewCycleOutputModel,
)
from ebiose.core.models.exceptions import EbioseCloudAuthError, EbioseCloudError

if TYPE_CHECKING:
    from ebiose.cloud_client.refactored_client import EbioseCloudClient


class EbioseAPIFacade:
    """Facade client providing a high-level interface to the EbioseCloud API."""

    _client: EbioseCloudClient | None = None

    @classmethod
    def set_client_credentials(
        self,
        base_url: str,
        api_key: str | None = None,
        bearer_token: str | None = None,
    ) -> None:
        """Set the API client credentials."""
        from ebiose.cloud_client.refactored_client import EbioseCloudClient

        self._client = EbioseCloudClient(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
        )
        logger.debug(f"EbioseCloudClient initialized for base URL: {base_url}")

    @classmethod
    def _get_client(cls) -> EbioseCloudClient:
        """Ensure the client is initialized."""
        if cls._client is None:
            msg = "Client not initialized. Call EbioseAPIFacade.set_client_credentials() first."
            raise EbioseCloudAuthError(msg)
        return cls._client

    @classmethod
    def _handle_request(cls, action_description: str, api_call, *args, **kwargs):
        """Generic request handler for the facade."""
        try:
            result = api_call(*args, **kwargs)
            return result
        except EbioseCloudError as e:
            logger.debug(f"An API error occurred while {action_description}: {e}")
            raise
        except Exception as e:
            logger.debug(f"An unexpected error occurred while {action_description}: {e}")
            raise

    # --- ApiKey Facade ---
    @classmethod
    def add_new_api_key(cls, data: ApiKeyInputModel) -> bool:
        """Add a new API key."""
        return cls._handle_request(
            "add new API key",
            cls._get_client().add_api_key,
            data=data,
        )

    # --- Forge Facade ---
    @classmethod
    def list_all_forges(cls) -> list[ForgeOutputModel]:
        """List all forges."""
        return cls._handle_request(
            "list all forges",
            cls._get_client().get_forges,
        )

    @classmethod
    def add_new_forge(cls, data: ForgeInputModel) -> ForgeOutputModel:
        """Add a new forge."""
        return cls._handle_request(
            "add new forge",
            cls._get_client().add_forge,
            data=data,
        )

    @classmethod
    def get_specific_forge(cls, forge_uuid: str) -> ForgeOutputModel:
        """Get a specific forge."""
        return cls._handle_request(
            f"get forge {forge_uuid}",
            cls._get_client().get_forge,
            forge_uuid=forge_uuid,
        )

    @classmethod
    def modify_forge(
        cls,
        forge_uuid: str,
        data: ForgeInputModel,
    ) -> ForgeOutputModel:
        """Modify a forge."""
        return cls._handle_request(
            f"update forge {forge_uuid}",
            cls._get_client().update_forge,
            forge_uuid=forge_uuid,
            data=data,
        )

    @classmethod
    def remove_forge(cls, forge_uuid: str) -> None:
        """Remove a forge."""
        return cls._handle_request(
            f"delete forge {forge_uuid}",
            cls._get_client().delete_forge,
            forge_uuid=forge_uuid,
        )

    @classmethod
    def begin_new_forge_cycle(
        cls,
        forge_uuid: str,
        data: ForgeCycleInputModel,
        override_key: bool | None = None,
    ) -> NewCycleOutputModel:
        """Begin a new forge cycle."""
        return cls._handle_request(
            f"start new forge cycle for forge {forge_uuid}",
            cls._get_client().start_new_forge_cycle,
            forge_uuid=forge_uuid,
            data=data,
            override_key=override_key,
        )

    @classmethod
    def conclude_forge_cycle(
        cls,
        forge_cycle_uuid: str,
        agents_data: list[AgentInputModel],
    ) -> None:
        """Conclude a forge cycle."""
        return cls._handle_request(
            f"end forge cycle {forge_cycle_uuid}",
            cls._get_client().end_forge_cycle,
            forge_cycle_uuid=forge_cycle_uuid,
            agents_data=agents_data,
        )

    @classmethod
    def get_forge_cycle_spend(cls, forge_cycle_uuid: str) -> float:
        """Get forge cycle spend."""
        return cls._handle_request(
            f"get spend for forge cycle {forge_cycle_uuid}",
            cls._get_client().get_spend,
            forge_cycle_uuid=forge_cycle_uuid,
        )

    @classmethod
    def log_forge_cycle_usage(cls, forge_cycle_uuid: str, cost: float) -> None:
        """Log forge cycle usage."""
        return cls._handle_request(
            f"record usage for forge cycle {forge_cycle_uuid}",
            cls._get_client().record_forge_cycle_usage,
            forge_cycle_uuid=forge_cycle_uuid,
            cost=cost,
        )

    @classmethod
    def pick_agents_for_forge_cycle(
        cls,
        forge_cycle_uuid: str,
        nb_agents: int,
    ) -> list[AgentOutputModel]:
        """Pick agents for forge cycle."""
        return cls._handle_request(
            f"select agents for forge cycle {forge_cycle_uuid}",
            cls._get_client().select_agents_for_forge_cycle,
            forge_cycle_uuid=forge_cycle_uuid,
            nb_agents=nb_agents,
        )

    @classmethod
    def make_deduct_compute_banks_for_forge_cycle(
        cls,
        forge_cycle_uuid: str,
        deductions: dict[str, float],
    ) -> None:
        """Deduct compute banks for forge cycle."""
        return cls._handle_request(
            f"deduct compute banks for forge cycle {forge_cycle_uuid}",
            cls._get_client().deduct_compute_banks_for_forge_cycle,
            forge_cycle_uuid=forge_cycle_uuid,
            deductions=deductions,
        )

    @classmethod
    def add_agent_during_cycle(
        cls,
        forge_cycle_uuid: str,
        agent_data: AgentInputModel,
    ) -> AgentOutputModel:
        """Add a single agent during an active forge cycle."""
        return cls._handle_request(
            f"add agent to active forge cycle {forge_cycle_uuid}",
            cls._get_client().add_agent_during_forge_cycle,
            forge_cycle_uuid=forge_cycle_uuid,
            data=agent_data,
        )

    @classmethod
    def add_agents_during_cycle(
        cls,
        forge_cycle_uuid: str,
        agents_data: list[AgentInputModel],
    ) -> None:
        """Add multiple agents during an active forge cycle."""
        return cls._handle_request(
            f"add agents to active forge cycle {forge_cycle_uuid}",
            cls._get_client().add_agents_during_forge_cycle,
            forge_cycle_uuid=forge_cycle_uuid,
            agents_data=agents_data,
        )

    # --- Logging Facade ---
    @classmethod
    def log_message(cls, data: LogEntryInputModel) -> LogEntryOutputModel:
        """Send a log entry to the logging service."""
        return cls._handle_request(
            f"send log entry to index '{data.index}'",
            cls._get_client().add_log_entry,
            data=data,
        )
