import subprocess
from typing import Any


class CiscoCollector:

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        timeout: int = 5,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout

    def execute(self, command: str) -> str:
        ssh_command = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=NUL",
            "-o", "KexAlgorithms=+diffie-hellman-group14-sha1",
            "-o", "HostKeyAlgorithms=+ssh-rsa",
            "-o", "PubkeyAcceptedAlgorithms=+ssh-rsa",
            "-o", "Ciphers=+aes128-cbc",
            "-o", "MACs=+hmac-sha1,hmac-sha1-96,hmac-md5,hmac-md5-96",
            "-p", str(self.port),
            f"{self.username}@{self.host}",
            command,
        ]

        result = subprocess.run(
            ssh_command,
            input=f"{self.password}\n",
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "SSH command failed"
            )

        return result.stdout

    def collect(self) -> dict[str, Any]:
        try:
            version = self.execute(
                "show version"
            )

            interfaces = self.execute(
                "show ip interface brief"
            )

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