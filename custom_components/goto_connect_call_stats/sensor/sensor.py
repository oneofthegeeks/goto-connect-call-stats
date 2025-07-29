"""Sensor entities for GoTo Connect Call Stats integration."""

from datetime import datetime
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    DEFAULT_NAME,
    DOMAIN,
    SENSOR_AVERAGE_CALL_DURATION,
    SENSOR_CALL_DURATION,
    SENSOR_INCOMING_CALLS,
    SENSOR_MISSED_CALLS,
    SENSOR_MONTH_CALLS,
    SENSOR_OUTGOING_CALLS,
    SENSOR_TODAY_CALLS,
    SENSOR_TOTAL_CALLS,
    SENSOR_WEEK_CALLS,
)


class GoToConnectCallStatsSensor(CoordinatorEntity, SensorEntity):
    """Base class for GoTo Connect Call Stats sensors."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "goto_connect_call_stats")},
            name=DEFAULT_NAME,
            manufacturer="GoTo Connect",
            model="Call Statistics",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        data = self.coordinator.data
        if not data:
            return {}

        return {
            "last_updated": data.get("last_updated"),
            "user_info": data.get("user_info", {}),
        }


class GoToConnectTotalCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for total calls today."""

    _attr_name = "Total Calls Today"
    _attr_unique_id = f"{DOMAIN}_total_calls"
    _attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("total_calls", 0)


class GoToConnectIncomingCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for incoming calls today."""

    _attr_name = "Incoming Calls Today"
    _attr_unique_id = f"{DOMAIN}_incoming_calls"
    _attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("incoming_calls", 0)


class GoToConnectOutgoingCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for outgoing calls today."""

    _attr_name = "Outgoing Calls Today"
    _attr_unique_id = f"{DOMAIN}_outgoing_calls"
    _attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("outgoing_calls", 0)


class GoToConnectMissedCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for missed calls today."""

    _attr_name = "Missed Calls Today"
    _attr_unique_id = f"{DOMAIN}_missed_calls"
    _attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("missed_calls", 0)


class GoToConnectCallDurationSensor(GoToConnectCallStatsSensor):
    """Sensor for total call duration today."""

    _attr_name = "Total Call Duration Today"
    _attr_unique_id = f"{DOMAIN}_call_duration"
    _attr_native_unit_of_measurement = "seconds"

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("total_duration", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        data = self.coordinator.data
        if data:
            duration_minutes = data.get("total_duration", 0) / 60
            attrs["duration_minutes"] = round(duration_minutes, 2)
            attrs["duration_hours"] = round(duration_minutes / 60, 2)
        return attrs


class GoToConnectAverageCallDurationSensor(GoToConnectCallStatsSensor):
    """Sensor for average call duration today."""

    _attr_name = "Average Call Duration Today"
    _attr_unique_id = f"{DOMAIN}_average_call_duration"
    _attr_native_unit_of_measurement = "seconds"

    @property
    def native_value(self) -> Optional[float]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return round(data.get("average_duration", 0), 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        data = self.coordinator.data
        if data:
            avg_minutes = data.get("average_duration", 0) / 60
            attrs["average_minutes"] = round(avg_minutes, 2)
        return attrs


class GoToConnectTodayCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for today's call statistics."""

    _attr_name = "Today's Call Statistics"
    _attr_unique_id = f"{DOMAIN}_today_calls"

    @property
    def native_value(self) -> Optional[str]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        
        today_data = data.get("today", {})
        total = today_data.get("total", 0)
        return f"{total} calls today"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        data = self.coordinator.data
        if data:
            today_data = data.get("today", {})
            attrs.update({
                "today_total": today_data.get("total", 0),
                "today_incoming": today_data.get("incoming", 0),
                "today_outgoing": today_data.get("outgoing", 0),
                "today_missed": today_data.get("missed", 0),
                "today_average_duration": today_data.get("average_duration", 0),
            })
        return attrs


class GoToConnectWeekCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for this week's call statistics."""

    _attr_name = "This Week's Call Statistics"
    _attr_unique_id = f"{DOMAIN}_week_calls"

    @property
    def native_value(self) -> Optional[str]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        
        week_data = data.get("week", {})
        total = week_data.get("total", 0)
        return f"{total} calls this week"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        data = self.coordinator.data
        if data:
            week_data = data.get("week", {})
            attrs.update({
                "week_total": week_data.get("total", 0),
                "week_incoming": week_data.get("incoming", 0),
                "week_outgoing": week_data.get("outgoing", 0),
                "week_missed": week_data.get("missed", 0),
                "week_average_duration": week_data.get("average_duration", 0),
            })
        return attrs


class GoToConnectMonthCallsSensor(GoToConnectCallStatsSensor):
    """Sensor for this month's call statistics."""

    _attr_name = "This Month's Call Statistics"
    _attr_unique_id = f"{DOMAIN}_month_calls"

    @property
    def native_value(self) -> Optional[str]:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        
        month_data = data.get("month", {})
        total = month_data.get("total", 0)
        return f"{total} calls this month"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        data = self.coordinator.data
        if data:
            month_data = data.get("month", {})
            attrs.update({
                "month_total": month_data.get("total", 0),
                "month_incoming": month_data.get("incoming", 0),
                "month_outgoing": month_data.get("outgoing", 0),
                "month_missed": month_data.get("missed", 0),
                "month_average_duration": month_data.get("average_duration", 0),
            })
        return attrs 