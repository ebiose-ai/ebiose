import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyInputModel")


@_attrs_define
class ApiKeyInputModel:
    """
    Attributes:
        user_uuid (Union[None, Unset, str]):
        expiration_date (Union[Unset, datetime.datetime]):
    """

    user_uuid: Union[None, Unset, str] = UNSET
    expiration_date: Union[Unset, datetime.datetime] = UNSET

    def to_dict(self) -> dict[str, Any]:
        user_uuid: Union[None, Unset, str]
        if isinstance(self.user_uuid, Unset):
            user_uuid = UNSET
        else:
            user_uuid = self.user_uuid

        expiration_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_date, Unset):
            expiration_date = self.expiration_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if user_uuid is not UNSET:
            field_dict["userUuid"] = user_uuid
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_user_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_uuid = _parse_user_uuid(d.pop("userUuid", UNSET))

        _expiration_date = d.pop("expirationDate", UNSET)
        expiration_date: Union[Unset, datetime.datetime]
        if isinstance(_expiration_date, Unset):
            expiration_date = UNSET
        else:
            expiration_date = isoparse(_expiration_date)

        api_key_input_model = cls(
            user_uuid=user_uuid,
            expiration_date=expiration_date,
        )

        return api_key_input_model
