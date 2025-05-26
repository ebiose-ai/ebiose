import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SelfApiKeyInputModel")


@_attrs_define
class SelfApiKeyInputModel:
    """
    Attributes:
        expiration_date (Union[Unset, datetime.datetime]):
    """

    expiration_date: Union[Unset, datetime.datetime] = UNSET

    def to_dict(self) -> dict[str, Any]:
        expiration_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_date, Unset):
            expiration_date = self.expiration_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _expiration_date = d.pop("expirationDate", UNSET)
        expiration_date: Union[Unset, datetime.datetime]
        if isinstance(_expiration_date, Unset):
            expiration_date = UNSET
        else:
            expiration_date = isoparse(_expiration_date)

        self_api_key_input_model = cls(
            expiration_date=expiration_date,
        )

        return self_api_key_input_model
