from dataclasses import dataclass
from datetime import datetime, timedelta


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
