import asyncio

from aiohttp import web

from cactus_client_notifications.server.endpoint_store import EndpointStore
from cactus_client_notifications.server.settings import ServerSettings, ServerStats

APPKEY_NOTIFICATION_STORE = web.AppKey("notification-store", EndpointStore)
APPKEY_SERVER_SETTINGS = web.AppKey("server-settings", ServerSettings)
APPKEY_PERIODIC_TASK = web.AppKey("periodic-task", asyncio.Task)
APPKEY_SERVER_STATS = web.AppKey("server-stats", ServerStats)
