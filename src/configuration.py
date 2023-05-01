import json
import os
from typing import Any
import yaml
from events.emitter import EventEmitter

from utils import dict_merge
from const import (
    DEFAULT_REPORT_INTERVAL,
    DEFAULT_BATTERY_WARNING_THRESHOLD,
    DEFAULT_BATTERY_VOLTAGE_MINIMUM,
    DEFAULT_BATTERY_VOLTAGE_MAXIMUM,
    DEFAULT_INA_I2C_ADDRESS,
    DEFAULT_INA_SHUNT_OHMS,
    DEFAULT_INA_MAX_EXPECTED_AMPS,
    DEFAULT_INA_MONITOR_INTERVAL,
)


class DynamicConfiguration:
    data: dict[str, Any]

    event: EventEmitter = EventEmitter()

    _dynamic_file: str

    def __init__(self, dynamic_file: str):
        self._dynamic_file = dynamic_file

        self.data = self._load()

        self.event.on(event_name="write", function=self.write)

    def _load(self):
        """Load dynamic configuration file"""

        dynamic_file_defaults = {
            "report_interval": DEFAULT_REPORT_INTERVAL,
            "battery_warning_threshold": DEFAULT_BATTERY_WARNING_THRESHOLD,
            "battery_voltage_minimum": DEFAULT_BATTERY_VOLTAGE_MINIMUM,
            "battery_voltage_maximum": DEFAULT_BATTERY_VOLTAGE_MAXIMUM,
        }

        if not os.path.exists(self._dynamic_file):
            with open(self._dynamic_file, "w") as file:
                json.dump(dynamic_file_defaults, file)

        with open(self._dynamic_file, "r") as file:
            dynamic_file_override = json.load(file)

        return {**dynamic_file_defaults, **dynamic_file_override}

    def write(self):
        """Write dynamic configuration file"""

        with open(self._dynamic_file, "w") as file:
            json.dump(self.data, file)


class LinkedConfiguration:
    static: dict[str, Any]
    dynamic: DynamicConfiguration

    _static_file: str
    _dynamic_file: str

    def __init__(self, static_file: str, dynamic_file: str):
        self._static_file = static_file
        self._dynamic_file = dynamic_file

        self.static = self._load()
        self.dynamic = DynamicConfiguration(self._dynamic_file)

    def _load(self):
        """Load static configuration file, and override defaults."""
        with open(self._static_file, "r") as static_file:
            static_file_override = yaml.safe_load(static_file)

        static_file_defaults = {
            "mqtt": {
                "broker": "127.0.0.1",
                "port": 1883,
                "user": "test",
                "password": "test",
                "client_id": "Red Reactor",
                "base_topic": "redreactor",
                "version": 3,
                "transport": "tcp",
                "timeout": 120,
                "topic": {
                    "state": "state",
                    "status": "status",
                    "set": "set",
                },
                "exit_on_fail": True,
            },
            "hostname": {"name": "redreactor", "pretty": "Red Reactor"},
            "homeassistant": {
                "discovery": True,
                "topic": "homeassistant",
                "discovery_interval": 120,
                "expire_after": 120,
            },
            "status": {
                "online": "online",
                "offline": "offline",
                # "startup_error": "RED_REACTOR_STARTUP_ERROR",
                # "current_range_error": "RED_REACTOR_CURRENT_RANGE_ERROR",
            },
            "fields": {
                "voltage": {
                    "name": "voltage",
                    "pretty": "Voltage",
                    "type": "sensor",
                    "unit": "V",
                    "device_class": "voltage",
                    "suggested_display_precision": 2,
                },
                "current": {
                    "name": "current",
                    "pretty": "Current",
                    "type": "sensor",
                    "unit": "mA",
                    "device_class": "current",
                    "suggested_display_precision": 2,
                },
                "battery_level": {
                    "name": "battery_level",
                    "pretty": "Battery Level",
                    "type": "sensor",
                    "unit": "%",
                    "device_class": "battery",
                },
                "external_power": {
                    "name": "external_power",
                    "pretty": "External Power",
                    "type": "binary_sensor",
                    "device_class": "plug",
                    "entity_category": "diagnostic",
                },
                "cpu_temperature": {
                    "name": "cpu_temperature",
                    "pretty": "CPU Temperature",
                    "type": "sensor",
                    "unit": "°C",
                    "device_class": "temperature",
                    "entity_category": "diagnostic",
                },
                "cpu_stat": {
                    "name": "cpu_stat",
                    "pretty": "CPU Stat",
                    "type": "sensor",
                    "entity_category": "diagnostic",
                },
                "battery_warning_threshold": {
                    "name": "battery_warning_threshold",
                    "pretty": "Battery Warning",
                    "type": "number",
                    "unit": "%",
                    "device_class": "battery",
                    "entity_category": "diagnostic",
                    "min": 0,
                    "max": 100,
                    "mode": "box",
                    "step": 1,
                },
                "battery_voltage_minimum": {
                    "name": "battery_voltage_minimum",
                    "pretty": "Battery Voltage Minimum",
                    "type": "number",
                    "unit": "V",
                    "device_class": "voltage",
                    "entity_category": "diagnostic",
                    "min": 2.5,
                    "max": 4.5,
                    "mode": "box",
                    "step": 0.1,
                },
                "battery_voltage_maximum": {
                    "name": "battery_voltage_maximum",
                    "pretty": "Battery Voltage Maximum",
                    "type": "number",
                    "unit": "V",
                    "device_class": "voltage",
                    "entity_category": "diagnostic",
                    "min": 2.5,
                    "max": 4.5,
                    "mode": "box",
                    "step": 0.1,
                },
                "report_interval": {
                    "name": "report_interval",
                    "pretty": "Report Interval",
                    "type": "number",
                    "unit": "s",
                    "entity_category": "diagnostic",
                    "min": 5,
                    "max": 300,
                    "mode": "box",
                    "step": 5,
                },
                "restart": {
                    "name": "restart",
                    "pretty": "Restart",
                    "type": "button",
                    "entity_category": "diagnostic",
                },
                "shutdown": {
                    "name": "shutdown",
                    "pretty": "Shutdown",
                    "type": "button",
                    "entity_category": "diagnostic",
                },
            },
            "ina": {
                "address": DEFAULT_INA_I2C_ADDRESS,
                "shunt_ohms": DEFAULT_INA_SHUNT_OHMS,
                "max_expected_amps": DEFAULT_INA_MAX_EXPECTED_AMPS,
                "monitor_interval": DEFAULT_INA_MONITOR_INTERVAL,
            },
            "system": {
                "shutdown": "sudo shutdown 0 -h",
                "restart": "sudo shutdown 0 -r",
            },
        }

        dict_merge(static_file_defaults, static_file_override)
        return static_file_defaults  # Overwritten any different values with the ones that came from the static file
