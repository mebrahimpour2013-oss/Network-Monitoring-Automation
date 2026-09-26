import os

from dotenv import load_dotenv

from src.monitoring.engine import calculate_overall_status, monitor_device
from src.monitoring.html_reporter import save_html_report
from src.monitoring.logger import setup_logger
from src.monitoring.models import Device
from src.monitoring.reporter import save_json_report


load_dotenv()


def main() -> None:
    logger = setup_logger()

    mikrotik_host = os.getenv("MIKROTIK_HOST")
    mikrotik_username = os.getenv("MIKROTIK_USERNAME")
    mikrotik_password = os.getenv("MIKROTIK_PASSWORD")
    mikrotik_api_port = int(
        os.getenv("MIKROTIK_API_PORT", "8728")
    )

    cisco_host = os.getenv("CISCO_HOST")
    cisco_username = os.getenv("CISCO_USERNAME")
    cisco_password = os.getenv("CISCO_PASSWORD")
    cisco_ssh_port = int(
        os.getenv("CISCO_SSH_PORT", "22")
    )

    if not mikrotik_host:
        raise ValueError(
            "MIKROTIK_HOST is not configured in .env"
        )

    devices = [
        Device(
            name="MikroTik-Lab",
            host=mikrotik_host,
            device_type="mikrotik",
            ports=[8728],
            metadata={
                "username": mikrotik_username,
                "password": mikrotik_password,
                "api_port": mikrotik_api_port,
            },
        ),
        Device(
            name="Cisco-Lab",
            host=cisco_host,
            device_type="cisco",
            ports=[22],
            metadata={
                "username": cisco_username,
                "password": cisco_password,
                "ssh_port": cisco_ssh_port,
            },
        ),
        Device(
            name="Google-DNS",
            host="8.8.8.8",
            device_type="network",
            ports=[53],
        ),
        Device(
            name="Cloudflare-DNS",
            host="1.1.1.1",
            device_type="network",
            ports=[53],
        ),
    ]

    for device in devices:
        print(
            f"\nDevice: {device.name} "
            f"({device.host})"
        )

        logger.info(
            "Starting monitoring for %s (%s)",
            device.name,
            device.host,
        )

        results = monitor_device(device)

        overall_status = calculate_overall_status(results)

        print(
            f"Overall Status: "
            f"{overall_status.value}"
        )

        json_report = save_json_report(
            device,
            results,
        )

        html_report = save_html_report(
            device,
            results,
        )

        print(
            f"JSON report saved: "
            f"{json_report}"
        )

        print(
            f"HTML report saved: "
            f"{html_report}"
        )

        logger.info(
            "Overall status for %s: %s",
            device.name,
            overall_status.value,
        )

        logger.info(
            "Monitoring completed for %s",
            device.name,
        )

        for result in results:
            print(
                f"[{result.status.value}] "
                f"{result.name}: "
                f"{result.message}"
            )


if __name__ == "__main__":
    main()