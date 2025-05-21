from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.role import Role
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserInputModel")


@_attrs_define
class UserInputModel:
    """
    Attributes:
        role (Union[Unset, Role]):
        firstname (Union[None, Unset, str]):
        lastname (Union[None, Unset, str]):
        email (Union[None, Unset, str]):
        github_id (Union[None, Unset, str]):
        credits_limit (Union[Unset, float]):
    """

    role: Union[Unset, Role] = UNSET
    firstname: Union[None, Unset, str] = UNSET
    lastname: Union[None, Unset, str] = UNSET
    email: Union[None, Unset, str] = UNSET
    github_id: Union[None, Unset, str] = UNSET
    credits_limit: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        role: Union[Unset, int] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        firstname: Union[None, Unset, str]
        if isinstance(self.firstname, Unset):
            firstname = UNSET
        else:
            firstname = self.firstname

        lastname: Union[None, Unset, str]
        if isinstance(self.lastname, Unset):
            lastname = UNSET
        else:
            lastname = self.lastname

        email: Union[None, Unset, str]
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        github_id: Union[None, Unset, str]
        if isinstance(self.github_id, Unset):
            github_id = UNSET
        else:
            github_id = self.github_id

        credits_limit = self.credits_limit

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if firstname is not UNSET:
            field_dict["firstname"] = firstname
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if email is not UNSET:
            field_dict["email"] = email
        if github_id is not UNSET:
            field_dict["githubId"] = github_id
        if credits_limit is not UNSET:
            field_dict["creditsLimit"] = credits_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _role = d.pop("role", UNSET)
        role: Union[Unset, Role]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = Role(_role)

        def _parse_firstname(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        firstname = _parse_firstname(d.pop("firstname", UNSET))

        def _parse_lastname(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        lastname = _parse_lastname(d.pop("lastname", UNSET))

        def _parse_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email = _parse_email(d.pop("email", UNSET))

        def _parse_github_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        github_id = _parse_github_id(d.pop("githubId", UNSET))

        credits_limit = d.pop("creditsLimit", UNSET)

        user_input_model = cls(
            role=role,
            firstname=firstname,
            lastname=lastname,
            email=email,
            github_id=github_id,
            credits_limit=credits_limit,
        )

        return user_input_model
