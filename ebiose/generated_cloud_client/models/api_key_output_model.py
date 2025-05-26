import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_output_model import UserOutputModel


T = TypeVar("T", bound="ApiKeyOutputModel")


@_attrs_define
class ApiKeyOutputModel:
    """
    Attributes:
        uuid (Union[None, Unset, str]):
        key (Union[None, Unset, str]):
        created_at (Union[Unset, datetime.datetime]):
        expiration_date (Union[Unset, datetime.datetime]):
        user (Union[Unset, UserOutputModel]):
    """

    uuid: Union[None, Unset, str] = UNSET
    key: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    expiration_date: Union[Unset, datetime.datetime] = UNSET
    user: Union[Unset, "UserOutputModel"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[None, Unset, str]
        if isinstance(self.uuid, Unset):
            uuid = UNSET
        else:
            uuid = self.uuid

        key: Union[None, Unset, str]
        if isinstance(self.key, Unset):
            key = UNSET
        else:
            key = self.key

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        expiration_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiration_date, Unset):
            expiration_date = self.expiration_date.isoformat()

        user: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if key is not UNSET:
            field_dict["key"] = key
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if expiration_date is not UNSET:
            field_dict["expirationDate"] = expiration_date
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_output_model import UserOutputModel

        d = dict(src_dict)

        def _parse_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        uuid = _parse_uuid(d.pop("uuid", UNSET))

        def _parse_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        key = _parse_key(d.pop("key", UNSET))

        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _expiration_date = d.pop("expirationDate", UNSET)
        expiration_date: Union[Unset, datetime.datetime]
        if isinstance(_expiration_date, Unset):
            expiration_date = UNSET
        else:
            expiration_date = isoparse(_expiration_date)

        _user = d.pop("user", UNSET)
        user: Union[Unset, UserOutputModel]
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = UserOutputModel.from_dict(_user)

        api_key_output_model = cls(
            uuid=uuid,
            key=key,
            created_at=created_at,
            expiration_date=expiration_date,
            user=user,
        )

        return api_key_output_model
