from time import perf_counter

import requests
from ping3 import ping

from .models import CheckResult, CheckStatus


def check_ping(host: str, timeout: int = 3) -> CheckResult:
    start = perf_counter()

    try:
        latency = ping(host, timeout=timeout, unit="ms")

        if latency is None:
            return CheckResult(
                name="ping",
                status=CheckStatus.DOWN,
                message=f"Host {host} is unreachable",
            )

        elapsed = round((perf_counter() - start) * 1000, 2)

        return CheckResult(
            name="ping",
            status=CheckStatus.UP,
            message=f"Host {host} is reachable",
            value=round(latency, 2),
            details={"latency_ms": round(latency, 2), "check_time_ms": elapsed},
        )

    except Exception as exc:
        return CheckResult(
            name="ping",
            status=CheckStatus.DOWN,
            message=f"Ping check failed: {exc}",
        )


def check_tcp_port(
    host: str,
    port: int,
    timeout: int = 3,
) -> CheckResult:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return CheckResult(
                name=f"tcp_{port}",
                status=CheckStatus.UP,
                message=f"TCP port {port} is open",
                value=port,
            )

    except (socket.timeout, ConnectionRefusedError, OSError) as exc:
        return CheckResult(
            name=f"tcp_{port}",
            status=CheckStatus.DOWN,
            message=f"TCP port {port} is unavailable: {exc}",
            value=port,
        )


def check_http(
    url: str,
    timeout: int = 5,
) -> CheckResult:
    try:
        response = requests.get(url, timeout=timeout)

        if response.ok:
            status = CheckStatus.UP
        else:
            status = CheckStatus.WARNING

        return CheckResult(
            name="http",
            status=status,
            message=f"HTTP status: {response.status_code}",
            value=response.status_code,
            details={
                "url": url,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            },
        )

    except requests.RequestException as exc:
        return CheckResult(
            name="http",
            status=CheckStatus.DOWN,
            message=f"HTTP check failed: {exc}",
            details={"url": url},
        )