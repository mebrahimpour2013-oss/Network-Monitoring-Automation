import json
from datetime import datetime, timezone
from pathlib import Path

from .engine import calculate_overall_status
from .models import CheckResult, Device


def save_json_report(
    device: Device,
    results: list[CheckResult],
    output_dir: str = "reports",
) -> Path:
    overall_status = calculate_overall_status(results)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device": {
            "name": device.name,
            "host": device.host,
            "type": device.device_type,
        },
        "overall_status": overall_status.value,
        "checks": [
            {
                "name": result.name,
                "status": result.status.value,
                "message": result.message,
                "value": result.value,
                "details": result.details,
            }
            for result in results
        ],
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{device.name}_report.json"
    report_file = output_path / filename

    report_file.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return report_file