from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewCycleOutputModel")


@_attrs_define
class NewCycleOutputModel:
    """
    Attributes:
        lite_llm_key (Union[None, Unset, str]):
        forge_cycle_uuid (Union[None, Unset, str]):
    """

    lite_llm_key: Union[None, Unset, str] = UNSET
    forge_cycle_uuid: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        lite_llm_key: Union[None, Unset, str]
        if isinstance(self.lite_llm_key, Unset):
            lite_llm_key = UNSET
        else:
            lite_llm_key = self.lite_llm_key

        forge_cycle_uuid: Union[None, Unset, str]
        if isinstance(self.forge_cycle_uuid, Unset):
            forge_cycle_uuid = UNSET
        else:
            forge_cycle_uuid = self.forge_cycle_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if lite_llm_key is not UNSET:
            field_dict["liteLLMKey"] = lite_llm_key
        if forge_cycle_uuid is not UNSET:
            field_dict["forgeCycleUuid"] = forge_cycle_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_lite_llm_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        lite_llm_key = _parse_lite_llm_key(d.pop("liteLLMKey", UNSET))

        def _parse_forge_cycle_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        forge_cycle_uuid = _parse_forge_cycle_uuid(d.pop("forgeCycleUuid", UNSET))

        new_cycle_output_model = cls(
            lite_llm_key=lite_llm_key,
            forge_cycle_uuid=forge_cycle_uuid,
        )

        return new_cycle_output_model
