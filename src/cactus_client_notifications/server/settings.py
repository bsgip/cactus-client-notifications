from dataclasses import dataclass, field
from datetime import datetime, timedelta

from cactus_client_notifications.server.time import utc_now


@dataclass(frozen=True)
class ServerSettings:
    port: int  # The app port that is being listened on
    public_server_url: str  # The public facing URL that all endpoints will be exposed under
    mount_point: str  # The path prefix that all served endpoints (and API endpoint endpoints) will be exposed under

    max_endpoint_idle_duration: (
        timedelta  # How long can an endpoint go without receiving a request before being removed
    )
    max_endpoint_duration: timedelta  # How long can an endpoint go for without being shutdown
    cleanup_frequency: timedelta  # How often to check for expired endpoints
    started_at: datetime

    max_active_endpoints: int  # How many endpoints can be managed at the same time
    max_endpoint_notifications: int  # How many notifications can an endpoint cache before dropping requests


@dataclass
class ServerStats:
    created_at: datetime = field(default_factory=utc_now)
    total_notifications: int = 0  # How many notifications have landed at the webhook since the server started
    total_notification_errors: int = 0  # How many exceptions caused by creating notification
    total_created_webhooks: int = 0  # How many webhooks have been created
    total_created_webhook_errors: int = 0  # How many exception caused by incoming webhook notifications
    total_collections: int = 0  # How many times has collect been called
    total_collection_errors: int = 0  # How many collect errors have been raised
    total_deletes: int = 0  # How many times has delete been called
    total_delete_errors: int = 0  # How many delete errors have been raised
    total_configures: int = 0  # How many times has the configure endpoint been called
    total_configure_errors: int = 0  # How many configure errors have been raised
