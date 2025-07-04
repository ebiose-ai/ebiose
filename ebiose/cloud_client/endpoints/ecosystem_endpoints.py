"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import AgentInputModel, AgentOutputModel, EcosystemOutputModel

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class EcosystemInputModel:
    """Input model for creating or updating an ecosystem."""
    
    def __init__(self, community_credits_available: float):
        self.communityCreditsAvailable = community_credits_available


class EcosystemEndpoints:
    """Ecosystem management endpoints."""
    
    def __init__(self, client: BaseHTTPClient) -> None:
        self.client = client
    
    def create_ecosystem(self, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Create a new ecosystem."""
        return EcosystemOutputModel(**self.client.request("POST", "/ecosystems", json_data=data))
    
    def list_ecosystems(self) -> list[EcosystemOutputModel]:
        """List all ecosystems."""
        return [EcosystemOutputModel(**item) for item in self.client.request("GET", "/ecosystems")]
    
    def get_ecosystem(self, uuid: str) -> EcosystemOutputModel:
        """Get a specific ecosystem."""
        return EcosystemOutputModel(**self.client.request("GET", f"/ecosystems/{uuid}"))
    
    def update_ecosystem(self, uuid: str, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Update an ecosystem."""
        return EcosystemOutputModel(**self.client.request("PUT", f"/ecosystems/{uuid}", json_data=data))
    
    def delete_ecosystem(self, uuid: str) -> None:
        """Delete an ecosystem."""
        self.client.request("DELETE", f"/ecosystems/{uuid}")
    
    def add_agents_to_ecosystem(self, ecosystem_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Add multiple agents to an ecosystem."""
        self.client.request("POST", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agents_data)
    
    def list_agents_in_ecosystem(self, ecosystem_uuid: str) -> list[AgentOutputModel]:
        """List all agents in an ecosystem."""
        return [AgentOutputModel(**item) for item in self.client.request("GET", f"/ecosystems/{ecosystem_uuid}/agents")]
    
    def delete_agents_from_ecosystem(self, ecosystem_uuid: str, agent_uuids: list[str]) -> None:
        """Delete multiple agents from an ecosystem."""
        self.client.request("DELETE", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agent_uuids)
    
    def get_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str) -> AgentOutputModel:
        """Get a specific agent within an ecosystem."""
        return AgentOutputModel(**self.client.request("GET", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}"))
    
    def update_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Update an agent within an ecosystem."""
        return AgentOutputModel(**self.client.request("PUT", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}", json_data=agent_data))
    
    def add_single_agent_to_ecosystem(self, ecosystem_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Add a single agent to an ecosystem."""
        return AgentOutputModel(**self.client.request("POST", f"/ecosystems/{ecosystem_uuid}/agent", json_data=agent_data))
