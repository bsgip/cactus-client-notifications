import http
import logging

from aiohttp import ContentTypeError, web

from cactus_client_notifications.schema import (
    URI_ENDPOINT,
    CollectEndpointResponse,
    ConfigureEndpointRequest,
    CreateEndpointRequest,
    CreateEndpointResponse,
)
from cactus_client_notifications.server.endpoint_store import (
    NotificationException,
    generate_collected_notification,
)
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


async def post_manage_endpoint_list(request: web.Request) -> web.Response:
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
        logger.error("Error creating endpoint", exc_info=exc)
        return web.Response(status=exc.status_code, text=str(exc))

    create_response = CreateEndpointResponse(
        endpoint_id=endpoint_id,
        fully_qualified_endpoint=generate_public_uri(request.app[APPKEY_SERVER_SETTINGS], endpoint_id),
    )

    return web.Response(status=http.HTTPStatus.CREATED, content_type="application/json", text=create_response.to_json())


async def get_manage_endpoint(request: web.Request) -> web.Response:
    """Performs a collection of notifications for the requested endpoint id. This will "consume" all notifications
    that are collected.

    Args:
        request: An aiohttp.web.Request instance.

    Returns:
        aiohttp.web.Response: Encodes a CollectEndpointResponse on success

        a 200 (OK) on success - yielding a CollectEndpointResponse as JSON
        a 404 (NOT_FOUND) if the endpoint has been deleted or the endpoint_id is invalid
    """

    endpoint_id = request.match_info.get("endpoint_id")
    if not endpoint_id:
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="endpoint_id couldn't be extracted from the path.")

    logger.info(f"Collecting endpoint {endpoint_id} for {request.remote}")

    try:
        collected_notifications = await request.app[APPKEY_NOTIFICATION_STORE].collect_notifications(endpoint_id)
    except NotificationException as exc:
        logger.error(f"Error updating config for {endpoint_id}", exc_info=exc)
        return web.Response(status=exc.status_code, text=str(exc))

    collect_response = CollectEndpointResponse(
        notifications=collected_notifications,
    )

    return web.Response(status=http.HTTPStatus.OK, content_type="application/json", text=collect_response.to_json())


async def put_manage_endpoint(request: web.Request) -> web.Response:
    """Updates the settings for an existing endpoint. Expects a ConfigureEndpointRequest in the request body

    Args:
        request: An aiohttp.web.Request instance.

    Returns:
        aiohttp.web.Response: Encodes a CreateEndpointResponse on success

        a 204 (NO_CONTENT) on success.
        a 404 (NOT_FOUND) if the endpoint has been deleted or the endpoint_id is invalid
    """

    endpoint_id = request.match_info.get("endpoint_id")
    if not endpoint_id:
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="endpoint_id couldn't be extracted from the path.")

    try:
        raw_json = await request.text()
    except ContentTypeError:
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="Missing JSON body")

    configure_request = ConfigureEndpointRequest.from_json(raw_json)
    if isinstance(configure_request, list):
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="Singular ConfigureEndpointRequest is required.")

    logger.info(f"Configuring endpoint {endpoint_id} with {configure_request} for {request.remote}")

    try:
        await request.app[APPKEY_NOTIFICATION_STORE].update_endpoint(endpoint_id, enabled=configure_request.enabled)
    except NotificationException as exc:
        logger.error(f"Error configuring {endpoint_id} with {configure_request}", exc_info=exc)
        return web.Response(status=exc.status_code, text=str(exc))

    return web.Response(status=http.HTTPStatus.NO_CONTENT)


async def delete_manage_endpoint(request: web.Request) -> web.Response:
    """Deletes an existing endpoint based on the endpoint_id in the path. All uncollected notifications will be lost.

    Args:
        request: An aiohttp.web.Request instance.

    Returns:
        aiohttp.web.Response: Encodes a CreateEndpointResponse on success

        a 204 (NO_CONTENT) on success.
        a 404 (NOT_FOUND) if the endpoint has been deleted or the endpoint_id is invalid
    """

    endpoint_id = request.match_info.get("endpoint_id")
    if not endpoint_id:
        return web.Response(status=http.HTTPStatus.BAD_REQUEST, text="endpoint_id couldn't be extracted from the path.")

    logger.info(f"Deleting endpoint {endpoint_id} for {request.remote}")

    try:
        await request.app[APPKEY_NOTIFICATION_STORE].try_delete_endpoint(endpoint_id)
    except NotificationException as exc:
        logger.error(f"Error deleting {endpoint_id}", exc_info=exc)
        return web.Response(status=exc.status_code, text=str(exc))

    return web.Response(status=http.HTTPStatus.NO_CONTENT)


async def webhook_endpoint(request: web.Request) -> web.Response:
    """This is the endpoint that will handle ALL incoming 2030.5 notifications from the utility server. It will try
    to report success for everything and log the contents of the incoming request.

    Args:
        request: An aiohttp.web.Request instance.

    Returns:
        aiohttp.web.Response: Encodes a CreateEndpointResponse on success

        a 200 (OK) on success.
        a 404 (NOT_FOUND) if the endpoint has been deleted or the endpoint_id is invalid
        a 500 (INTERNAL_SERVER_ERROR) if the endpoint has been disabled
        a 507 (INSUFFICIENT_STORAGE) if the endpoint has too many uncollected notifications
    """

    endpoint_id = request.match_info.get("endpoint_id")
    if not endpoint_id:
        return web.Response(status=http.HTTPStatus.NOT_FOUND)

    try:
        collected_notification = await generate_collected_notification(request)
    except Exception as exc:
        logger.error(f"Error parsing incoming webhook request for {endpoint_id} from {request.remote}", exc_info=exc)
        return web.Response(status=http.HTTPStatus.BAD_REQUEST)

    logger.info(
        f"{collected_notification.method} notification ({len(collected_notification.body)}) at {endpoint_id}"
        + f"from {request.remote}."
    )

    try:
        await request.app[APPKEY_NOTIFICATION_STORE].add_notification(endpoint_id, collected_notification)
    except NotificationException as exc:
        logger.error(f"Error adding notification to {endpoint_id}", exc_info=exc)
        return web.Response(status=exc.status_code, text=str(exc))

    return web.Response(status=http.HTTPStatus.OK)
