"""Sensor platform for GoTo Connect Call Stats integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensor import (
    GoToConnectTotalCallsSensor,
    GoToConnectIncomingCallsSensor,
    GoToConnectOutgoingCallsSensor,
    GoToConnectMissedCallsSensor,
    GoToConnectCallDurationSensor,
    GoToConnectAverageCallDurationSensor,
    GoToConnectTodayCallsSensor,
    GoToConnectWeekCallsSensor,
    GoToConnectMonthCallsSensor,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GoTo Connect Call Stats sensors from a config entry."""
    coordinator = hass.data["goto_connect_call_stats"][entry.entry_id]

    sensors = [
        GoToConnectTotalCallsSensor(coordinator),
        GoToConnectIncomingCallsSensor(coordinator),
        GoToConnectOutgoingCallsSensor(coordinator),
        GoToConnectMissedCallsSensor(coordinator),
        GoToConnectCallDurationSensor(coordinator),
        GoToConnectAverageCallDurationSensor(coordinator),
        GoToConnectTodayCallsSensor(coordinator),
        GoToConnectWeekCallsSensor(coordinator),
        GoToConnectMonthCallsSensor(coordinator),
    ]

    async_add_entities(sensors) 