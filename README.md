# Network Monitoring & Health Check Automation

A production-oriented Python automation project for monitoring the operational health of multi-vendor network infrastructure.

The system performs read-only health checks against MikroTik RouterOS and Cisco IOS devices, evaluates operational conditions, and generates structured JSON and HTML health reports.

The project is designed around real network operations rather than a simulated lab scenario, with a modular architecture that allows additional vendors and monitoring capabilities to be introduced without changing the core monitoring workflow.

## Business Problem

Routine network health checks often require engineers to connect to multiple devices, verify connectivity, inspect resource utilization, review interfaces, and manually document the results.

This approach becomes inefficient as the number of devices increases and makes consistent reporting more difficult.

This project automates these operational checks and provides a standardized health assessment for heterogeneous network infrastructure.

## Solution

The monitoring engine provides a common workflow across different network vendors:

```text
Network Devices
      |
      v
Connectivity Checks
      |
      v
Vendor-specific Collection
      |
      v
Data Parsing & Normalization
      |
      v
Health Evaluation
      |
      +-------------------+
      |                   |
      v                   v
   JSON Report        HTML Report
      |
      v
   Monitoring Log
   ```

Vendor-specific collectors handle the differences between network platforms while the monitoring engine maintains a consistent health evaluation workflow.

Key Capabilities

Network Availability

ICMP reachability checks

Response latency measurement

TCP service availability checks

Device connectivity validation


MikroTik Monitoring

RouterOS API connectivity

Device identity

RouterOS version

CPU utilization

Memory utilization

System uptime

Interface status


Cisco Monitoring

SSH connectivity

Cisco IOS version

CPU utilization

Memory utilization

System uptime

Interface operational state

Interface protocol health


Health Evaluation

Monitoring results are normalized into three operational states:

Status	Meaning

UP	Normal operational condition
WARNING	Non-critical operational issue detected
DOWN	Critical failure or unavailable service


CPU and memory thresholds are configurable through the monitoring configuration.

Interface health is evaluated separately from simple interface availability so inactive interfaces are not automatically treated as failures.

Architecture

Monitoring Engine
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
   MikroTik Collector                Cisco Collector
      RouterOS API                     SSH / Netmiko
          |                                 |
          +----------------+----------------+
                           |
                           v
                  Data Parsing Layer
                           |
                           v
                   Health Evaluation
                           |
             +-------------+-------------+
             |                           |
             v                           v
       JSON Reporter              HTML Reporter
             |                           |
             +-------------+-------------+
                           |
                           v
                       Logging

The architecture separates:

Device communication

Vendor-specific data collection

Output parsing

Health evaluation

Report generation

Logging


This separation makes the monitoring engine easier to extend and maintain.

Project Structure
Network-Monitoring-Automation/
│
├── config/
│   └── monitoring.json
│
├── src/
│   └── monitoring/
│       ├── checks.py
│       ├── cisco.py
│       ├── cisco_parser.py
│       ├── config.py
│       ├── engine.py
│       ├── html_reporter.py
│       ├── logger.py
│       ├── mikrotik.py
│       ├── models.py
│       └── reporter.py
│
├── reports/
│
├── .env
├── .gitignore
├── main.py
└── requirements.txt

Configuration

Device credentials are loaded through environment variables and are not embedded in the source code.

Example:

MIKROTIK_HOST=<device-ip>
MIKROTIK_USERNAME=<username>
MIKROTIK_PASSWORD=<password>
MIKROTIK_API_PORT=8728

CISCO_HOST=<device-ip>
CISCO_USERNAME=<username>
CISCO_PASSWORD=<password>
CISCO_SSH_PORT=22

Health thresholds are maintained separately from application logic.

Example:

{
  "thresholds": {
    "cpu": {
      "warning": 75,
      "critical": 90
    },
    "memory": {
      "warning": 80,
      "critical": 90
    }
  }
}

Reporting

Each monitoring run produces structured output for the monitored devices.

JSON

JSON reports are designed for machine-readable results and future integration with other systems.

Example:

{
  "device": "network-device",
  "overall_status": "UP",
  "checks": [
    {
      "name": "ping",
      "status": "UP"
    },
    {
      "name": "cpu",
      "status": "UP"
    }
  ]
}

HTML

HTML reports provide a human-readable operational summary including:

Overall device status

Number of checks

UP / WARNING / DOWN counts

Individual check results

Values and diagnostic details

Report generation timestamp


Logging

The application maintains structured monitoring logs containing:

Monitoring start

Monitoring completion

Device status

Execution events

Operational errors


This provides a basic audit trail for monitoring executions.

Security

The monitoring design follows a read-only operational model.

Security-related considerations include:

Credentials are supplied through environment variables.

.env is excluded from version control.

No device configuration changes are performed.

Monitoring operations only collect operational information.

Generated reports and local logs are excluded from version control.


Technology Stack

Python 3

MikroTik RouterOS API

Netmiko

Cisco IOS

Netmiko

Requests

Ping3

python-dotenv

JSON

HTML/CSS

Git


Validation

The project has been validated against physical network infrastructure and real device outputs.

Validation included:

MikroTik RouterOS 7.x

Cisco Catalyst 2960S

Cisco IOS 15.2(2)E9

ICMP connectivity

TCP service availability

MikroTik API connectivity

Cisco SSH connectivity

CPU and memory collection

Interface state collection

JSON report generation

HTML report generation

Application logging


The validation environment was based on actual network devices rather than simulated responses.

Operational Example

A monitoring execution can produce results similar to:

Device: MikroTik
Overall Status: UP

[UP] ping
[UP] tcp_8728
[UP] mikrotik_api
[UP] routeros_version
[UP] cpu
[UP] memory
[UP] uptime
[UP] interfaces

and:

Device: Cisco
Overall Status: WARNING

[UP] ping
[UP] tcp_22
[UP] cisco_ssh
[UP] cisco_version
[UP] cisco_cpu
[UP] cisco_memory
[WARNING] cisco_interfaces
[UP] cisco_uptime

The warning state demonstrates that the system does not simply report device reachability; it evaluates operational conditions collected from the device.

Scope

The current implementation focuses on core network health monitoring and reporting.

Potential future integrations may include:

Scheduled monitoring

Alerting

SNMP-based collection

Historical metrics

Additional network vendors

Centralized monitoring dashboards


These capabilities are outside the current implementation scope.

Related Projects

This project is part of a broader network automation portfolio:

Network Automation — configuration backup and operational information collection

MikroTik Network Compliance — security and configuration compliance assessment
Network Monitoring & Health Check Automation — operational monitoring and health reporting


Together, these projects demonstrate automation across configuration management, security/compliance, and network operations.

Author

Mohammad Ebrahimpour

Network & IT Infrastructure Specialist

Network Automation | Network Security | Server & Cloud Administration
