import re
from typing import Any


def parse_version(output: str) -> dict[str, Any]:
    result: dict[str, Any] = {}

    hostname_match = re.search(
        r"^(\S+)\s+uptime is",
        output,
        re.MULTILINE,
    )

    version_match = re.search(
        r"Version\s+([\w().-]+)",
        output,
    )

    uptime_match = re.search(
        r"uptime is\s+(.+)",
        output,
        re.IGNORECASE,
    )

    if hostname_match:
        result["hostname"] = hostname_match.group(1)

    if version_match:
        result["version"] = version_match.group(1)

    if uptime_match:
        result["uptime"] = uptime_match.group(1).strip()

    return result


def parse_cpu(output: str) -> dict[str, Any]:
    match = re.search(
        r"CPU utilization for five seconds:\s*(\d+)%/(\d+)%",
        output,
        re.IGNORECASE,
    )

    if not match:
        return {}

    return {
        "cpu_5_seconds_percent": int(match.group(1)),
        "cpu_interrupt_percent": int(match.group(2)),
    }


def parse_memory(output: str) -> dict[str, Any]:
    match = re.search(
        r"Processor Pool Total:\s*(\d+)\s+Used:\s*(\d+)\s+Free:\s*(\d+)",
        output,
        re.IGNORECASE,
    )

    if not match:
        return {}

    total = int(match.group(1))
    used = int(match.group(2))
    free = int(match.group(3))

    usage_percent = (
        round((used / total) * 100, 2)
        if total
        else 0
    )

    return {
        "total": total,
        "used": used,
        "free": free,
        "usage_percent": usage_percent,
    }


def parse_interfaces(output: str) -> list[dict[str, Any]]:
    interfaces = []

    pattern = re.compile(
        r"^(\S+)\s+"
        r"(\S+)\s+"
        r"\S+\s+"
        r"\S+\s+"
        r"(\S+)\s+"
        r"(\S+)\s*$",
        re.MULTILINE,
    )

    for match in pattern.finditer(output):
        if match.group(1).lower() == "interface":
            continue

        interfaces.append(
            {
                "interface": match.group(1),
                "ip_address": match.group(2),
                "status": match.group(3).lower(),
                "protocol": match.group(4).lower(),
            }
        )

    return interfaces