from typing import Any

from librouteros import connect


class MikroTikCollector:
    """
    Read-only collector for MikroTik RouterOS devices.
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 8728,
        timeout: int = 5,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.api = None

    def connect(self) -> None:
        self.api = connect(
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            timeout=self.timeout,
        )

    def close(self) -> None:
        if self.api is not None:
            try:
                self.api.close()
            except Exception:
                pass
            finally:
                self.api = None

    def _ensure_connected(self) -> None:
        if self.api is None:
            self.connect()

    def get_identity(self) -> dict[str, Any]:
        self._ensure_connected()

        rows = list(
            self.api.path("/system/identity").select()
        )

        return rows[0] if rows else {}

    def get_resource(self) -> dict[str, Any]:
        self._ensure_connected()

        rows = list(
            self.api.path("/system/resource").select()
        )

        return rows[0] if rows else {}

    def get_interfaces(self) -> list[dict[str, Any]]:
        self._ensure_connected()

        return list(
            self.api.path("/interface").select()
        )

    def collect(self) -> dict[str, Any]:
        """
        Collect operational health information from MikroTik.
        No configuration changes are performed.
        """
        try:
            self.connect()

            identity = self.get_identity()
            resource = self.get_resource()
            interfaces = self.get_interfaces()

            return {
                "status": "UP",
                "identity": identity,
                "resource": resource,
                "interfaces": interfaces,
            }

        except Exception as exc:
            return {
                "status": "DOWN",
                "error": str(exc),
            }

        finally:
            self.close()