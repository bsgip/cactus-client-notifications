import os

import pytest
from aiohttp import ClientSession, ClientTimeout
from assertical.fixtures.environment import environment_snapshot

from cactus_client_notifications.server.main import create_app


def marker_to_env(request: pytest.FixtureRequest, var_name: str) -> None:
    marker = request.node.get_closest_marker(var_name)
    if marker is not None:
        os.environ[var_name] = str(marker.args[0])


@pytest.fixture
async def client_session(aiohttp_client, request: pytest.FixtureRequest):
    with environment_snapshot():
        marker_to_env(request, "APP_PORT")
        marker_to_env(request, "SERVER_URL")
        marker_to_env(request, "MOUNT_POINT")
        marker_to_env(request, "MAX_IDLE_DURATION_SECONDS")
        marker_to_env(request, "MAX_DURATION_SECONDS")
        marker_to_env(request, "MAX_ACTIVE_ENDPOINTS")
        marker_to_env(request, "MAX_ENDPOINT_NOTIFICATIONS")
        marker_to_env(request, "CLEANUP_FREQUENCY_SECONDS")

        async with await aiohttp_client(create_app()) as app:
            async with ClientSession(base_url=app.make_url("/"), timeout=ClientTimeout(30)) as session:
                yield session
