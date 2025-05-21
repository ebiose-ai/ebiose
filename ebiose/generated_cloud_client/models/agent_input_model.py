from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_engine_input_model import AgentEngineInputModel


T = TypeVar("T", bound="AgentInputModel")


@_attrs_define
class AgentInputModel:
    """
    Attributes:
        name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        architect_agent_uuid (Union[None, Unset, str]):
        genetic_operator_agent_uuid (Union[None, Unset, str]):
        agent_engine (Union[Unset, AgentEngineInputModel]):
        description_embedding (Union[None, Unset, str]):
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    architect_agent_uuid: Union[None, Unset, str] = UNSET
    genetic_operator_agent_uuid: Union[None, Unset, str] = UNSET
    agent_engine: Union[Unset, "AgentEngineInputModel"] = UNSET
    description_embedding: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        architect_agent_uuid: Union[None, Unset, str]
        if isinstance(self.architect_agent_uuid, Unset):
            architect_agent_uuid = UNSET
        else:
            architect_agent_uuid = self.architect_agent_uuid

        genetic_operator_agent_uuid: Union[None, Unset, str]
        if isinstance(self.genetic_operator_agent_uuid, Unset):
            genetic_operator_agent_uuid = UNSET
        else:
            genetic_operator_agent_uuid = self.genetic_operator_agent_uuid

        agent_engine: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.agent_engine, Unset):
            agent_engine = self.agent_engine.to_dict()

        description_embedding: Union[None, Unset, str]
        if isinstance(self.description_embedding, Unset):
            description_embedding = UNSET
        else:
            description_embedding = self.description_embedding

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if architect_agent_uuid is not UNSET:
            field_dict["architectAgentUuid"] = architect_agent_uuid
        if genetic_operator_agent_uuid is not UNSET:
            field_dict["geneticOperatorAgentUuid"] = genetic_operator_agent_uuid
        if agent_engine is not UNSET:
            field_dict["agentEngine"] = agent_engine
        if description_embedding is not UNSET:
            field_dict["descriptionEmbedding"] = description_embedding

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_engine_input_model import AgentEngineInputModel

        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_architect_agent_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        architect_agent_uuid = _parse_architect_agent_uuid(d.pop("architectAgentUuid", UNSET))

        def _parse_genetic_operator_agent_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        genetic_operator_agent_uuid = _parse_genetic_operator_agent_uuid(d.pop("geneticOperatorAgentUuid", UNSET))

        _agent_engine = d.pop("agentEngine", UNSET)
        agent_engine: Union[Unset, AgentEngineInputModel]
        if isinstance(_agent_engine, Unset):
            agent_engine = UNSET
        else:
            agent_engine = AgentEngineInputModel.from_dict(_agent_engine)

        def _parse_description_embedding(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description_embedding = _parse_description_embedding(d.pop("descriptionEmbedding", UNSET))

        agent_input_model = cls(
            name=name,
            description=description,
            architect_agent_uuid=architect_agent_uuid,
            genetic_operator_agent_uuid=genetic_operator_agent_uuid,
            agent_engine=agent_engine,
            description_embedding=description_embedding,
        )

        return agent_input_model
