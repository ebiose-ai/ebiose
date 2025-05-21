from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EcosystemInputModel")


@_attrs_define
class EcosystemInputModel:
    """
    Attributes:
        community_credits_available (Union[Unset, float]):
    """

    community_credits_available: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        community_credits_available = self.community_credits_available

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if community_credits_available is not UNSET:
            field_dict["communityCreditsAvailable"] = community_credits_available

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        community_credits_available = d.pop("communityCreditsAvailable", UNSET)

        ecosystem_input_model = cls(
            community_credits_available=community_credits_available,
        )

        return ecosystem_input_model
