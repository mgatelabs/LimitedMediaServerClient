"""mediaserver — Python client for the media/volume server API.

Usage:
    from mediaserver import MediaServerClient

    # From a config file:
    client = MediaServerClient("config.json")

    # From environment variables (no file needed):
    client = MediaServerClient()

    client.login()
    books = client.books.list_books()
    client.media.move_file(file_id, folder_id)

See mediaserver._config for the full list of supported env vars.
"""

from pathlib import Path

from mediaserver._config  import ServerConfig
from mediaserver._session import SessionStore, Feature
from mediaserver._http    import HttpLayer
from mediaserver.auth     import AuthClient
from mediaserver.media    import MediaClient
from mediaserver.volume   import VolumeClient
from mediaserver.process  import ProcessClient
from mediaserver.plugin   import PluginClient

__all__ = ["MediaServerClient", "Feature"]


class MediaServerClient:
    """Entry point for the media server Python client.

    Constructs and wires all sub-clients.  All auth state lives on this
    instance, so multiple clients can point at different servers.

    Attributes:
        auth    -- AuthClient    (login, renew, session info)
        media   -- MediaClient   (folders, files, upload, download, preview)
        books   -- VolumeClient  (books, chapters, images, tags)
        process -- ProcessClient (background tasks)
        plugins -- PluginClient  (plugin discovery and execution)
    """

    def __init__(self, config_path: str | Path | None = None):
        """Create a client.

        config_path — path to config.json.  Pass None (the default) to rely
        entirely on environment variables.  MEDIASERVER_CONFIG env var takes
        precedence over config_path when both are set.
        """
        config  = ServerConfig(config_path)
        session = SessionStore()
        http    = HttpLayer(config, session)
        auth    = AuthClient(http, config, session)
        http.set_auth_client(auth)

        self.auth    = auth
        self.media   = MediaClient(http)
        self.books   = VolumeClient(http)
        self.process = ProcessClient(http)
        self.plugins = PluginClient(http)

    def login(self) -> dict:
        """Convenience passthrough to auth.login()."""
        return self.auth.login()

    def get_session_info(self) -> dict:
        """Convenience passthrough to auth.get_session_info()."""
        return self.auth.get_session_info()
