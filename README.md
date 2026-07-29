
# AppLog-Simulator

Version 1.1

Application log generator for monitoring tests.

Designed for:

- Checkmk Logwatch
- Nagios
- Zabbix log monitoring
- SIEM testing


## Features

- Multiple applications
- Generic log generation
- Template based logs
- Smart mode
- Failure scenarios


## Supported scenarios

- database_failure
- disk_full
- memory_leak
- network_timeout
- authentication_failure
- kafka_down
- rabbitmq_unavailable


## Configuration example


```yaml

name: my-service

output_log: /var/log/my-service.log

mode: smart


scenario:

 enabled: true

 type: database_failure

 every: 900

