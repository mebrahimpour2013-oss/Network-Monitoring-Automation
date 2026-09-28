from typing import Any

from netmiko import ConnectHandler


class CiscoCollector:
    """
    Read-only collector for Cisco IOS devices using Netmiko.
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        timeout: int = 10,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.connection = None

    def connect(self) -> None:
        self.connection = ConnectHandler(
            device_type="cisco_ios",
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            conn_timeout=self.timeout,
            auth_timeout=self.timeout,
            banner_timeout=self.timeout,
        )

    def close(self) -> None:
        if self.connection is not None:
            try:
                self.connection.disconnect()
            except Exception:
                pass
            finally:
                self.connection = None

    def execute(self, command: str) -> str:
        if self.connection is None:
            self.connect()

        return self.connection.send_command(command)

    def collect(self) -> dict[str, Any]:
        try:
            self.connect()

            version = self.execute("show version")
            interfaces = self.execute("show ip interface brief")
            cpu = self.execute(
                "show processes cpu | include CPU utilization"
            )
            memory = self.execute(
                "show processes memory | include Processor"
            )
            uptime = self.execute(
                "show version | include uptime"
            )

            return {
                "status": "UP",
                "version": version,
                "interfaces": interfaces,
                "cpu": cpu,
                "memory": memory,
                "uptime": uptime,
            }

        except Exception as exc:
            return {
                "status": "DOWN",
                "error": str(exc),
            }

        finally:
            self.close()