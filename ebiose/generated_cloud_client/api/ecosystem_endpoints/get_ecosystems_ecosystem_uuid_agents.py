from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_output_model import AgentOutputModel
from ...types import Response


def _get_kwargs(
    ecosystem_uuid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/ecosystems/{ecosystem_uuid}/agents",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, list["AgentOutputModel"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AgentOutputModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, list["AgentOutputModel"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ecosystem_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, list["AgentOutputModel"]]]:
    """
    Args:
        ecosystem_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AgentOutputModel']]]
    """

    kwargs = _get_kwargs(
        ecosystem_uuid=ecosystem_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ecosystem_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, list["AgentOutputModel"]]]:
    """
    Args:
        ecosystem_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AgentOutputModel']]
    """

    return sync_detailed(
        ecosystem_uuid=ecosystem_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    ecosystem_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, list["AgentOutputModel"]]]:
    """
    Args:
        ecosystem_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, list['AgentOutputModel']]]
    """

    kwargs = _get_kwargs(
        ecosystem_uuid=ecosystem_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ecosystem_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, list["AgentOutputModel"]]]:
    """
    Args:
        ecosystem_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, list['AgentOutputModel']]
    """

    return (
        await asyncio_detailed(
            ecosystem_uuid=ecosystem_uuid,
            client=client,
        )
    ).parsed
