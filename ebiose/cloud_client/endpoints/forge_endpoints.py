"""Forge-related API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import (
    AgentInputModel,
    AgentOutputModel,
    ForgeCycleInputModel,
    ForgeInputModel,
    ForgeOutputModel,
    NewCycleOutputModel,
)

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class ForgeEndpoints:
    """Forge-related API endpoints."""

    def __init__(self, client: BaseHTTPClient) -> None:
        """Initialize forge endpoints."""
        self.client = client

    def get_forges(self) -> list[ForgeOutputModel]:
        """Get all forges."""
        response = self.client.request("GET", "/forges")
        return [ForgeOutputModel(**item) for item in response]

    def add_forge(self, data: ForgeInputModel) -> ForgeOutputModel:
        """Add a new forge."""
        response = self.client.request("POST", "/forges", json_data=data)
        return ForgeOutputModel(**response)

    def get_forge(self, forge_uuid: str) -> ForgeOutputModel:
        """Get a specific forge."""
        response = self.client.request("GET", f"/forges/{forge_uuid}")
        return ForgeOutputModel(**response)

    def update_forge(
        self, forge_uuid: str, data: ForgeInputModel
    ) -> ForgeOutputModel:
        """Update a forge."""
        response = self.client.request(
            "PUT", f"/forges/{forge_uuid}", json_data=data
        )
        return ForgeOutputModel(**response)

    def delete_forge(self, forge_uuid: str) -> None:
        """Delete a forge."""
        self.client.request("DELETE", f"/forges/{forge_uuid}")

    def start_new_forge_cycle(
        self,
        forge_uuid: str,
        data: ForgeCycleInputModel,
        override_key: bool | None = None,
    ) -> NewCycleOutputModel:
        """Start a new forge cycle."""
        params = {"overrideKey": override_key} if override_key is not None else {}
        response = self.client.request(
            "POST",
            f"/forges/{forge_uuid}/cycles/start",
            params=params,
            json_data=data,
        )
        return NewCycleOutputModel(**response)

    def end_forge_cycle(
        self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]
    ) -> None:
        """End a forge cycle."""
        self.client.request(
            "POST",
            f"/forges/cycles/{forge_cycle_uuid}/end",
            json_data=agents_data,
        )

    def get_spend(self, forge_cycle_uuid: str) -> float:
        """Get spend for a forge cycle."""
        return self.client.request(
            "GET", f"/forges/cycles/{forge_cycle_uuid}/spend"
        )

    def select_agents_for_forge_cycle(
        self, forge_cycle_uuid: str, nb_agents: int
    ) -> list[AgentOutputModel]:
        """Select agents for a forge cycle."""
        response = self.client.request(
            "GET",
            f"/forges/cycles/{forge_cycle_uuid}/select-agents",
            params={"nbAgents": nb_agents},
        )
        return [AgentOutputModel(**item) for item in response]

    def deduct_compute_banks_for_forge_cycle(
        self, forge_cycle_uuid: str, deductions: dict[str, float]
    ) -> None:
        """Deduct compute banks for a forge cycle."""
        self.client.request(
            "POST",
            f"/forges/cycles/{forge_cycle_uuid}/deduct-compute-banks",
            json_data=deductions,
        )

    def record_forge_cycle_usage(self, forge_cycle_uuid: str, cost: float) -> None:
        """Record usage for a forge cycle."""
        self.client.request(
            "POST",
            f"/forges/cycles/{forge_cycle_uuid}/usage",
            params={"cost": cost},
        )

    def add_agent_during_forge_cycle(
        self, forge_cycle_uuid: str, data: AgentInputModel
    ) -> AgentOutputModel:
        """Add agent during forge cycle."""
        response = self.client.request(
            "POST", f"/forges/cycles/{forge_cycle_uuid}/agent", json_data=data
        )
        return AgentOutputModel(**response)

    def add_agents_during_forge_cycle(
        self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]
    ) -> None:
        """Add agents during forge cycle."""
        self.client.request(
            "POST",
            f"/forges/cycles/{forge_cycle_uuid}/agents",
            json_data=agents_data,
        )
