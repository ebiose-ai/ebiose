from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentEngineInputModel")


@_attrs_define
class AgentEngineInputModel:
    """
    Attributes:
        engine_type (Union[None, Unset, str]):
        configuration (Union[None, Unset, str]):
    """

    engine_type: Union[None, Unset, str] = UNSET
    configuration: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        engine_type: Union[None, Unset, str]
        if isinstance(self.engine_type, Unset):
            engine_type = UNSET
        else:
            engine_type = self.engine_type

        configuration: Union[None, Unset, str]
        if isinstance(self.configuration, Unset):
            configuration = UNSET
        else:
            configuration = self.configuration

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if engine_type is not UNSET:
            field_dict["engineType"] = engine_type
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_engine_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        engine_type = _parse_engine_type(d.pop("engineType", UNSET))

        def _parse_configuration(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        configuration = _parse_configuration(d.pop("configuration", UNSET))

        agent_engine_input_model = cls(
            engine_type=engine_type,
            configuration=configuration,
        )

        return agent_engine_input_model
