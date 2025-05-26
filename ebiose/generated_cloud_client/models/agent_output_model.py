from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_engine_output_model import AgentEngineOutputModel
    from ..models.ecosystem_output_model import EcosystemOutputModel


T = TypeVar("T", bound="AgentOutputModel")


@_attrs_define
class AgentOutputModel:
    """
    Attributes:
        uuid (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        ecosystem (Union[Unset, EcosystemOutputModel]):
        architect_agent (Union[Unset, AgentOutputModel]):
        genetic_operator_agent (Union[Unset, AgentOutputModel]):
        agent_engine (Union[Unset, AgentEngineOutputModel]):
        description_embedding (Union[None, Unset, list[float]]):
        compute_bank_in_dollars (Union[Unset, float]):
    """

    uuid: Union[None, Unset, str] = UNSET
    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    ecosystem: Union[Unset, "EcosystemOutputModel"] = UNSET
    architect_agent: Union[Unset, "AgentOutputModel"] = UNSET
    genetic_operator_agent: Union[Unset, "AgentOutputModel"] = UNSET
    agent_engine: Union[Unset, "AgentEngineOutputModel"] = UNSET
    description_embedding: Union[None, Unset, list[float]] = UNSET
    compute_bank_in_dollars: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[None, Unset, str]
        if isinstance(self.uuid, Unset):
            uuid = UNSET
        else:
            uuid = self.uuid

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

        ecosystem: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ecosystem, Unset):
            ecosystem = self.ecosystem.to_dict()

        architect_agent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.architect_agent, Unset):
            architect_agent = self.architect_agent.to_dict()

        genetic_operator_agent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.genetic_operator_agent, Unset):
            genetic_operator_agent = self.genetic_operator_agent.to_dict()

        agent_engine: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.agent_engine, Unset):
            agent_engine = self.agent_engine.to_dict()

        description_embedding: Union[None, Unset, list[float]]
        if isinstance(self.description_embedding, Unset):
            description_embedding = UNSET
        elif isinstance(self.description_embedding, list):
            description_embedding = self.description_embedding

        else:
            description_embedding = self.description_embedding

        compute_bank_in_dollars = self.compute_bank_in_dollars

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if ecosystem is not UNSET:
            field_dict["ecosystem"] = ecosystem
        if architect_agent is not UNSET:
            field_dict["architectAgent"] = architect_agent
        if genetic_operator_agent is not UNSET:
            field_dict["geneticOperatorAgent"] = genetic_operator_agent
        if agent_engine is not UNSET:
            field_dict["agentEngine"] = agent_engine
        if description_embedding is not UNSET:
            field_dict["descriptionEmbedding"] = description_embedding
        if compute_bank_in_dollars is not UNSET:
            field_dict["computeBankInDollars"] = compute_bank_in_dollars

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_engine_output_model import AgentEngineOutputModel
        from ..models.ecosystem_output_model import EcosystemOutputModel

        d = dict(src_dict)

        def _parse_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        uuid = _parse_uuid(d.pop("uuid", UNSET))

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

        _ecosystem = d.pop("ecosystem", UNSET)
        ecosystem: Union[Unset, EcosystemOutputModel]
        if isinstance(_ecosystem, Unset):
            ecosystem = UNSET
        else:
            ecosystem = EcosystemOutputModel.from_dict(_ecosystem)

        _architect_agent = d.pop("architectAgent", UNSET)
        architect_agent: Union[Unset, AgentOutputModel]
        if isinstance(_architect_agent, Unset):
            architect_agent = UNSET
        else:
            architect_agent = AgentOutputModel.from_dict(_architect_agent)

        _genetic_operator_agent = d.pop("geneticOperatorAgent", UNSET)
        genetic_operator_agent: Union[Unset, AgentOutputModel]
        if isinstance(_genetic_operator_agent, Unset):
            genetic_operator_agent = UNSET
        else:
            genetic_operator_agent = AgentOutputModel.from_dict(_genetic_operator_agent)

        _agent_engine = d.pop("agentEngine", UNSET)
        agent_engine: Union[Unset, AgentEngineOutputModel]
        if isinstance(_agent_engine, Unset):
            agent_engine = UNSET
        else:
            agent_engine = AgentEngineOutputModel.from_dict(_agent_engine)

        def _parse_description_embedding(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                description_embedding_type_0 = cast(list[float], data)

                return description_embedding_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        description_embedding = _parse_description_embedding(d.pop("descriptionEmbedding", UNSET))

        compute_bank_in_dollars = d.pop("computeBankInDollars", UNSET)

        agent_output_model = cls(
            uuid=uuid,
            name=name,
            description=description,
            ecosystem=ecosystem,
            architect_agent=architect_agent,
            genetic_operator_agent=genetic_operator_agent,
            agent_engine=agent_engine,
            description_embedding=description_embedding,
            compute_bank_in_dollars=compute_bank_in_dollars,
        )

        return agent_output_model
