from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SelfUserInputModel")


@_attrs_define
class SelfUserInputModel:
    """
    Attributes:
        firstname (Union[None, Unset, str]):
        lastname (Union[None, Unset, str]):
        email (Union[None, Unset, str]):
        github_id (Union[None, Unset, str]):
        password (Union[None, Unset, str]):
    """

    firstname: Union[None, Unset, str] = UNSET
    lastname: Union[None, Unset, str] = UNSET
    email: Union[None, Unset, str] = UNSET
    github_id: Union[None, Unset, str] = UNSET
    password: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
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

        password: Union[None, Unset, str]
        if isinstance(self.password, Unset):
            password = UNSET
        else:
            password = self.password

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if firstname is not UNSET:
            field_dict["firstname"] = firstname
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if email is not UNSET:
            field_dict["email"] = email
        if github_id is not UNSET:
            field_dict["githubId"] = github_id
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

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

        def _parse_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        password = _parse_password(d.pop("password", UNSET))

        self_user_input_model = cls(
            firstname=firstname,
            lastname=lastname,
            email=email,
            github_id=github_id,
            password=password,
        )

        return self_user_input_model
