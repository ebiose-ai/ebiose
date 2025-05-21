from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_output_model import AgentOutputModel


T = TypeVar("T", bound="EcosystemOutputModel")


@_attrs_define
class EcosystemOutputModel:
    """
    Attributes:
        uuid (Union[None, Unset, str]):
        community_credits_available (Union[Unset, float]):
        agents (Union[None, Unset, list['AgentOutputModel']]):
    """

    uuid: Union[None, Unset, str] = UNSET
    community_credits_available: Union[Unset, float] = UNSET
    agents: Union[None, Unset, list["AgentOutputModel"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[None, Unset, str]
        if isinstance(self.uuid, Unset):
            uuid = UNSET
        else:
            uuid = self.uuid

        community_credits_available = self.community_credits_available

        agents: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.agents, Unset):
            agents = UNSET
        elif isinstance(self.agents, list):
            agents = []
            for agents_type_0_item_data in self.agents:
                agents_type_0_item = agents_type_0_item_data.to_dict()
                agents.append(agents_type_0_item)

        else:
            agents = self.agents

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if community_credits_available is not UNSET:
            field_dict["communityCreditsAvailable"] = community_credits_available
        if agents is not UNSET:
            field_dict["agents"] = agents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_output_model import AgentOutputModel

        d = dict(src_dict)

        def _parse_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        uuid = _parse_uuid(d.pop("uuid", UNSET))

        community_credits_available = d.pop("communityCreditsAvailable", UNSET)

        def _parse_agents(data: object) -> Union[None, Unset, list["AgentOutputModel"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                agents_type_0 = []
                _agents_type_0 = data
                for agents_type_0_item_data in _agents_type_0:
                    agents_type_0_item = AgentOutputModel.from_dict(agents_type_0_item_data)

                    agents_type_0.append(agents_type_0_item)

                return agents_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["AgentOutputModel"]], data)

        agents = _parse_agents(d.pop("agents", UNSET))

        ecosystem_output_model = cls(
            uuid=uuid,
            community_credits_available=community_credits_available,
            agents=agents,
        )

        return ecosystem_output_model
