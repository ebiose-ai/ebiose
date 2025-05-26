from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_output_model import UserOutputModel


T = TypeVar("T", bound="LoginOutputModel")


@_attrs_define
class LoginOutputModel:
    """
    Attributes:
        user (Union[Unset, UserOutputModel]):
        token (Union[None, Unset, str]):
    """

    user: Union[Unset, "UserOutputModel"] = UNSET
    token: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        user: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        token: Union[None, Unset, str]
        if isinstance(self.token, Unset):
            token = UNSET
        else:
            token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_output_model import UserOutputModel

        d = dict(src_dict)
        _user = d.pop("user", UNSET)
        user: Union[Unset, UserOutputModel]
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = UserOutputModel.from_dict(_user)

        def _parse_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        token = _parse_token(d.pop("token", UNSET))

        login_output_model = cls(
            user=user,
            token=token,
        )

        return login_output_model
