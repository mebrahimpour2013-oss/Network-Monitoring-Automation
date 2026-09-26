from .checks import check_ping, check_tcp_port
from .config import load_config
from .cisco import CiscoCollector
from .mikrotik import MikroTikCollector
from .models import CheckResult, CheckStatus, Device


def calculate_overall_status(
    results: list[CheckResult],
) -> CheckStatus:
    if any(
        result.status == CheckStatus.DOWN
        for result in results
    ):
        return CheckStatus.DOWN

    if any(
        result.status == CheckStatus.WARNING
        for result in results
    ):
        return CheckStatus.WARNING

    return CheckStatus.UP


def monitor_device(
    device: Device,
) -> list[CheckResult]:
    results: list[CheckResult] = []

    results.append(
        check_ping(device.host)
    )

    for port in device.ports:
        results.append(
            check_tcp_port(
                device.host,
                port,
            )
        )

    device_type = device.device_type.lower()

    if device_type == "mikrotik":
        results.extend(
            check_mikrotik(device)
        )

    elif device_type == "cisco":
        results.extend(
            check_cisco(device)
        )

    return results


def check_mikrotik(
    device: Device,
) -> list[CheckResult]:

    username = device.metadata.get(
        "username"
    )

    password = device.metadata.get(
        "password"
    )

    api_port = device.metadata.get(
        "api_port",
        8728,
    )

    if not username or not password:
        return [
            CheckResult(
                name="mikrotik_api",
                status=CheckStatus.WARNING,
                message=(
                    "MikroTik API credentials "
                    "are not configured"
                ),
            )
        ]

    config = load_config()

    cpu_warning = config[
        "thresholds"
    ][
        "cpu"
    ][
        "warning"
    ]

    cpu_critical = config[
        "thresholds"
    ][
        "cpu"
    ][
        "critical"
    ]

    memory_warning = config[
        "thresholds"
    ][
        "memory"
    ][
        "warning"
    ]

    memory_critical = config[
        "thresholds"
    ][
        "memory"
    ][
        "critical"
    ]

    collector = MikroTikCollector(
        host=device.host,
        username=username,
        password=password,
        port=api_port,
    )

    data = collector.collect()

    if data.get("status") == "DOWN":
        return [
            CheckResult(
                name="mikrotik_api",
                status=CheckStatus.DOWN,
                message=(
                    "MikroTik API check failed: "
                    f"{data.get('error', 'Unknown error')}"
                ),
            )
        ]

    results: list[CheckResult] = []

    results.append(
        CheckResult(
            name="mikrotik_api",
            status=CheckStatus.UP,
            message="MikroTik API is reachable",
        )
    )

    identity = data.get(
        "identity",
        {},
    )

    resource = data.get(
        "resource",
        {},
    )

    interfaces = data.get(
        "interfaces",
        [],
    )

    identity_name = identity.get(
        "name"
    )

    results.append(
        CheckResult(
            name="identity",
            status=(
                CheckStatus.UP
                if identity_name
                else CheckStatus.WARNING
            ),
            message=(
                f"Router identity: {identity_name}"
                if identity_name
                else "Router identity is unavailable"
            ),
            value=identity_name,
        )
    )

    version = resource.get(
        "version"
    )

    results.append(
        CheckResult(
            name="routeros_version",
            status=(
                CheckStatus.UP
                if version
                else CheckStatus.WARNING
            ),
            message=(
                f"RouterOS version: {version}"
                if version
                else "RouterOS version is unavailable"
            ),
            value=version,
        )
    )
    cpu_load = resource.get(
        "cpu-load"
    )

    if cpu_load is None:
        results.append(
            CheckResult(
                name="cpu",
                status=CheckStatus.WARNING,
                message=(
                    "CPU load information "
                    "is unavailable"
                ),
            )
        )

    else:
        try:
            cpu_value = float(
                cpu_load
            )

            if cpu_value >= cpu_critical:
                cpu_status = CheckStatus.DOWN
                cpu_message = (
                    f"CPU load is critical: "
                    f"{cpu_value:.1f}%"
                )

            elif cpu_value >= cpu_warning:
                cpu_status = CheckStatus.WARNING
                cpu_message = (
                    f"CPU load is high: "
                    f"{cpu_value:.1f}%"
                )

            else:
                cpu_status = CheckStatus.UP
                cpu_message = (
                    f"CPU load is normal: "
                    f"{cpu_value:.1f}%"
                )

            results.append(
                CheckResult(
                    name="cpu",
                    status=cpu_status,
                    message=cpu_message,
                    value=cpu_value,
                    details={
                        "cpu_load_percent": cpu_value,
                        "warning_threshold": cpu_warning,
                        "critical_threshold": cpu_critical,
                    },
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            results.append(
                CheckResult(
                    name="cpu",
                    status=CheckStatus.WARNING,
                    message=(
                        f"Invalid CPU load value: "
                        f"{cpu_load}"
                    ),
                )
            )

    total_memory = resource.get(
        "total-memory"
    )

    free_memory = resource.get(
        "free-memory"
    )

    if (
        total_memory is None
        or free_memory is None
    ):
        results.append(
            CheckResult(
                name="memory",
                status=CheckStatus.WARNING,
                message=(
                    "Memory information "
                    "is unavailable"
                ),
            )
        )

    else:
        try:
            total = float(
                total_memory
            )

            free = float(
                free_memory
            )

            if total <= 0:
                raise ValueError(
                    "Invalid total memory"
                )

            used = total - free

            usage_percent = (
                used / total
            ) * 100

            if (
                usage_percent
                >= memory_critical
            ):
                memory_status = (
                    CheckStatus.DOWN
                )

                memory_message = (
                    "Memory usage is critical: "
                    f"{usage_percent:.1f}%"
                )

            elif (
                usage_percent
                >= memory_warning
            ):
                memory_status = (
                    CheckStatus.WARNING
                )

                memory_message = (
                    "Memory usage is high: "
                    f"{usage_percent:.1f}%"
                )

            else:
                memory_status = (
                    CheckStatus.UP
                )

                memory_message = (
                    "Memory usage is normal: "
                    f"{usage_percent:.1f}%"
                )

            results.append(
                CheckResult(
                    name="memory",
                    status=memory_status,
                    message=memory_message,
                    value=round(
                        usage_percent,
                        2,
                    ),
                    details={
                        "total_memory": total,
                        "free_memory": free,
                        "used_memory": used,
                        "usage_percent": round(
                            usage_percent,
                            2,
                        ),
                        "warning_threshold": (
                            memory_warning
                        ),
                        "critical_threshold": (
                            memory_critical
                        ),
                    },
                )
            )

        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            results.append(
                CheckResult(
                    name="memory",
                    status=CheckStatus.WARNING,
                    message=(
                        "Invalid memory information"
                    ),
                )
            )

    uptime = resource.get(
        "uptime"
    )

    results.append(
        CheckResult(
            name="uptime",
            status=(
                CheckStatus.UP
                if uptime
                else CheckStatus.WARNING
            ),
            message=(
                f"Router uptime: {uptime}"
                if uptime
                else "Uptime information is unavailable"
            ),
            value=uptime,
        )
    )

    if interfaces:
        running_count = sum(
            1
            for interface in interfaces
            if interface.get(
                "running"
            ) not in (
                False,
                "false",
                "no",
            )
        )

        results.append(
            CheckResult(
                name="interfaces",
                status=CheckStatus.UP,
                message=(
                    f"{running_count} of "
                    f"{len(interfaces)} "
                    "interfaces are running"
                ),
                value=running_count,
                details={
                    "total_interfaces": len(
                        interfaces
                    ),
                    "running_interfaces": (
                        running_count
                    ),
                },
            )
        )

    return results


def check_cisco(
    device: Device,
) -> list[CheckResult]:

    username = device.metadata.get(
        "username"
    )

    password = device.metadata.get(
        "password"
    )

    ssh_port = device.metadata.get(
        "ssh_port",
        22,
    )

    if not username or not password:
        return [
            CheckResult(
                name="cisco_ssh",
                status=CheckStatus.WARNING,
                message=(
                    "Cisco SSH credentials "
                    "are not configured"
                ),
            )
        ]

    collector = CiscoCollector(
        host=device.host,
        username=username,
        password=password,
        port=ssh_port,
    )

    data = collector.collect()

    if data.get("status") == "DOWN":
        return [
            CheckResult(
                name="cisco_ssh",
                status=CheckStatus.DOWN,
                message=(
                    "Cisco SSH check failed: "
                    f"{data.get('error', 'Unknown error')}"
                ),
            )
        ]

    results: list[CheckResult] = []

    version_output = data.get(
        "version",
        "",
    )

    interfaces_output = data.get(
        "interfaces",
        "",
    )

    cpu_output = data.get(
        "cpu",
        "",
    )

    memory_output = data.get(
        "memory",
        "",
    )

    uptime_output = data.get(
        "uptime",
        "",
    )
    results.append(
        CheckResult(
            name="cisco_ssh",
            status=CheckStatus.UP,
            message="Cisco SSH is reachable",
        )
    )

    results.append(
        CheckResult(
            name="cisco_version",
            status=(
                CheckStatus.UP
                if version_output
                else CheckStatus.WARNING
            ),
            message=(
                "Cisco IOS version information collected"
                if version_output
                else (
                    "Cisco IOS version information "
                    "unavailable"
                )
            ),
            details={
                "output": version_output[:2000],
            },
        )
    )

    results.append(
        CheckResult(
            name="cisco_interfaces",
            status=(
                CheckStatus.UP
                if interfaces_output
                else CheckStatus.WARNING
            ),
            message=(
                "Cisco interface information collected"
                if interfaces_output
                else (
                    "Cisco interface information "
                    "unavailable"
                )
            ),
            details={
                "output": interfaces_output[:2000],
            },
        )
    )

    results.append(
        CheckResult(
            name="cisco_cpu",
            status=(
                CheckStatus.UP
                if cpu_output
                else CheckStatus.WARNING
            ),
            message=(
                "Cisco CPU information collected"
                if cpu_output
                else (
                    "Cisco CPU information "
                    "unavailable"
                )
            ),
            details={
                "output": cpu_output[:2000],
            },
        )
    )

    results.append(
        CheckResult(
            name="cisco_memory",
            status=(
                CheckStatus.UP
                if memory_output
                else CheckStatus.WARNING
            ),
            message=(
                "Cisco memory information collected"
                if memory_output
                else (
                    "Cisco memory information "
                    "unavailable"
                )
            ),
            details={
                "output": memory_output[:2000],
            },
        )
    )

    results.append(
        CheckResult(
            name="cisco_uptime",
            status=(
                CheckStatus.UP
                if uptime_output
                else CheckStatus.WARNING
            ),
            message=(
                "Cisco uptime information collected"
                if uptime_output
                else (
                    "Cisco uptime information "
                    "unavailable"
                )
            ),
            details={
                "output": uptime_output[:2000],
            },
        )
    )

    return results