import http
import logging

from aiohttp import ContentTypeError, web

from cactus_client_notifications.schema import (
    URI_ENDPOINT,
    CreateEndpointRequest,
    CreateEndpointResponse,
)
from cactus_client_notifications.server.endpoint_store import NotificationException
from cactus_client_notifications.server.settings import ServerSettings
from cactus_client_notifications.server.shared import (
    APPKEY_NOTIFICATION_STORE,
    APPKEY_SERVER_SETTINGS,
)

logger = logging.getLogger(__name__)


def path_join(*parts: str) -> str:
    joinable_parts: list[str] = []

    last: str | None = None
    for next in parts:
        next = next.strip()
        if not next:
            continue

        if last is None:
            joinable_parts.append(next)
            last = next
            continue

        # Here is where the join logic happens
        if last.endswith("/"):
            if next.startswith("/"):
                if len(next) == 1:
                    continue  # Don't add an empty string (once we strip the /)
                joinable_parts.append(next[1:])
            else:
                joinable_parts.append(next)
        else:
            if next.startswith("/"):
                joinable_parts.append(next)
            else:
                joinable_parts.append("/")
                joinable_parts.append(next)
        last = next

    return "".join(joinable_parts)


def generate_public_uri(server_settings: ServerSettings, endpoint_id: str) -> str:
    """Generates the public facing URI for a specific endpoint_id"""
    return path_join(
        server_settings.public_server_url, server_settings.mount_point, URI_ENDPOINT.format(endpoint_id=endpoint_id)
    )


async def handle_post_manage_endpoint_list(request: web.Request) -> web.Response:
    """Expects a CreateEndpointResponse to be included in the POST body. Creates a new endpoint

    Args:
        request: An aiohttp.web.Request instance.

    Returns:
        aiohttp.web.Response: Encodes a CreateEndpointResponse on success

        a 201 (CREATED) on success
        a 507 (INSUFFICIENT_STORAGE) if the webserver has too many notification endpoints at this moment
    """
    try:
        raw_json = await request.text()
    except ContentTypeError:
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="Missing JSON body")

    create_request = CreateEndpointRequest.from_json(raw_json)
    if isinstance(create_request, list):
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="Singular CreateEndpointRequest is required.")

    logger.info(f"Creating endpoint for Test ID {create_request.test_id} for {request.remote}")

    try:
        endpoint_id = await request.app[APPKEY_NOTIFICATION_STORE].create_endpoint()
    except NotificationException as exc:
        return web.Response(status=exc.status_code, text=str(exc))

    create_response = CreateEndpointResponse(
        endpoint_id=endpoint_id,
        fully_qualified_endpoint=generate_public_uri(request.app[APPKEY_SERVER_SETTINGS], endpoint_id),
    )

    return web.Response(status=http.HTTPStatus.CREATED, content_type="application/json", text=create_response.to_json())
