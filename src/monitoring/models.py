from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    WARNING = "WARNING"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    value: Any = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Device:
    name: str
    host: str
    device_type: str
    ports: list[int] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)