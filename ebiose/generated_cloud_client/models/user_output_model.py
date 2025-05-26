from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.role import Role
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_key_output_model import ApiKeyOutputModel


T = TypeVar("T", bound="UserOutputModel")


@_attrs_define
class UserOutputModel:
    """
    Attributes:
        uuid (Union[None, Unset, str]):
        role (Union[Unset, Role]):
        firstname (Union[None, Unset, str]):
        lastname (Union[None, Unset, str]):
        email (Union[None, Unset, str]):
        github_id (Union[None, Unset, str]):
        api_keys (Union[None, Unset, list['ApiKeyOutputModel']]):
        credits_limit (Union[Unset, float]):
        credits_used (Union[Unset, float]):
        available_credits (Union[Unset, float]):
    """

    uuid: Union[None, Unset, str] = UNSET
    role: Union[Unset, Role] = UNSET
    firstname: Union[None, Unset, str] = UNSET
    lastname: Union[None, Unset, str] = UNSET
    email: Union[None, Unset, str] = UNSET
    github_id: Union[None, Unset, str] = UNSET
    api_keys: Union[None, Unset, list["ApiKeyOutputModel"]] = UNSET
    credits_limit: Union[Unset, float] = UNSET
    credits_used: Union[Unset, float] = UNSET
    available_credits: Union[Unset, float] = UNSET

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[None, Unset, str]
        if isinstance(self.uuid, Unset):
            uuid = UNSET
        else:
            uuid = self.uuid

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

        api_keys: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.api_keys, Unset):
            api_keys = UNSET
        elif isinstance(self.api_keys, list):
            api_keys = []
            for api_keys_type_0_item_data in self.api_keys:
                api_keys_type_0_item = api_keys_type_0_item_data.to_dict()
                api_keys.append(api_keys_type_0_item)

        else:
            api_keys = self.api_keys

        credits_limit = self.credits_limit

        credits_used = self.credits_used

        available_credits = self.available_credits

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
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
        if api_keys is not UNSET:
            field_dict["apiKeys"] = api_keys
        if credits_limit is not UNSET:
            field_dict["creditsLimit"] = credits_limit
        if credits_used is not UNSET:
            field_dict["creditsUsed"] = credits_used
        if available_credits is not UNSET:
            field_dict["availableCredits"] = available_credits

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_output_model import ApiKeyOutputModel

        d = dict(src_dict)

        def _parse_uuid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        uuid = _parse_uuid(d.pop("uuid", UNSET))

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

        def _parse_api_keys(data: object) -> Union[None, Unset, list["ApiKeyOutputModel"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                api_keys_type_0 = []
                _api_keys_type_0 = data
                for api_keys_type_0_item_data in _api_keys_type_0:
                    api_keys_type_0_item = ApiKeyOutputModel.from_dict(api_keys_type_0_item_data)

                    api_keys_type_0.append(api_keys_type_0_item)

                return api_keys_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ApiKeyOutputModel"]], data)

        api_keys = _parse_api_keys(d.pop("apiKeys", UNSET))

        credits_limit = d.pop("creditsLimit", UNSET)

        credits_used = d.pop("creditsUsed", UNSET)

        available_credits = d.pop("availableCredits", UNSET)

        user_output_model = cls(
            uuid=uuid,
            role=role,
            firstname=firstname,
            lastname=lastname,
            email=email,
            github_id=github_id,
            api_keys=api_keys,
            credits_limit=credits_limit,
            credits_used=credits_used,
            available_credits=available_credits,
        )

        return user_output_model
