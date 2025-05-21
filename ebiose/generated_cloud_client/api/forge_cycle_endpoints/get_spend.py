from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs(
    forge_cycle_uuid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/forges/spend/{forge_cycle_uuid}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, float]]:
    if response.status_code == 200:
        response_200 = cast(float, response.json())
        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, float]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    forge_cycle_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, float]]:
    """
    Args:
        forge_cycle_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, float]]
    """

    kwargs = _get_kwargs(
        forge_cycle_uuid=forge_cycle_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    forge_cycle_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, float]]:
    """
    Args:
        forge_cycle_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, float]
    """

    return sync_detailed(
        forge_cycle_uuid=forge_cycle_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    forge_cycle_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, float]]:
    """
    Args:
        forge_cycle_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, float]]
    """

    kwargs = _get_kwargs(
        forge_cycle_uuid=forge_cycle_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    forge_cycle_uuid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, float]]:
    """
    Args:
        forge_cycle_uuid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, float]
    """

    return (
        await asyncio_detailed(
            forge_cycle_uuid=forge_cycle_uuid,
            client=client,
        )
    ).parsed
