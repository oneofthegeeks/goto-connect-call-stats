"""Coordinator for GoTo Connect Call Stats integration."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CALLS_API_URL,
    GOTO_API_BASE_URL,
    UPDATE_INTERVAL,
    USERS_API_URL,
)
from .oauth import GoToOAuth2Manager

_LOGGER = logging.getLogger(__name__)


class GoToConnectCallStatsCoordinator(DataUpdateCoordinator):
    """Coordinator for GoTo Connect Call Stats."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="GoTo Connect Call Stats",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self.oauth_manager = GoToOAuth2Manager(hass, entry)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data from GoTo Connect API."""
        try:
            # Load tokens
            if not self.oauth_manager.load_tokens():
                raise UpdateFailed("Failed to load authentication tokens")

            # Get headers for API requests
            headers = self.oauth_manager.get_headers()

            # Create session if needed
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()

            # Fetch call data
            call_stats = await self._fetch_call_stats(headers)
            
            return call_stats

        except Exception as err:
            _LOGGER.error("Error updating GoTo Connect Call Stats: %s", err)
            raise UpdateFailed(f"Error updating call stats: {err}") from err

    async def _fetch_call_stats(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Fetch call statistics from GoTo Connect API."""
        try:
            # Get user information first
            user_info = await self._fetch_user_info(headers)
            
            # Get call data for different time periods
            today_stats = await self._fetch_calls_for_period(headers, "today")
            week_stats = await self._fetch_calls_for_period(headers, "week")
            month_stats = await self._fetch_calls_for_period(headers, "month")
            
            # Calculate aggregated statistics
            total_calls = today_stats.get("total", 0)
            incoming_calls = today_stats.get("incoming", 0)
            outgoing_calls = today_stats.get("outgoing", 0)
            missed_calls = today_stats.get("missed", 0)
            
            # Calculate call duration statistics
            call_durations = today_stats.get("durations", [])
            total_duration = sum(call_durations) if call_durations else 0
            avg_duration = total_duration / len(call_durations) if call_durations else 0
            
            return {
                "user_info": user_info,
                "today": today_stats,
                "week": week_stats,
                "month": month_stats,
                "total_calls": total_calls,
                "incoming_calls": incoming_calls,
                "outgoing_calls": outgoing_calls,
                "missed_calls": missed_calls,
                "total_duration": total_duration,
                "average_duration": avg_duration,
                "last_updated": datetime.now().isoformat(),
            }
            
        except Exception as e:
            _LOGGER.error("Failed to fetch call statistics: %s", e)
            raise

    async def _fetch_user_info(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Fetch user information from GoTo Connect API."""
        try:
            url = f"{GOTO_API_BASE_URL}{USERS_API_URL}"
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.warning("Failed to fetch user info: %s", response.status)
                    return {}
        except Exception as e:
            _LOGGER.error("Error fetching user info: %s", e)
            return {}

    async def _fetch_calls_for_period(
        self, headers: Dict[str, str], period: str
    ) -> Dict[str, Any]:
        """Fetch call data for a specific time period."""
        try:
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=1)

            # Format dates for API
            start_str = start_date.isoformat() + "Z"
            end_str = end_date.isoformat() + "Z"

            # Build API URL with parameters
            url = f"{GOTO_API_BASE_URL}{CALLS_API_URL}"
            params = {
                "startTime": start_str,
                "endTime": end_str,
                "limit": 1000,  # Get maximum calls
            }

            async with self._session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_call_data(data)
                else:
                    _LOGGER.warning("Failed to fetch calls for %s: %s", period, response.status)
                    return self._get_empty_stats()

        except Exception as e:
            _LOGGER.error("Error fetching calls for %s: %s", period, e)
            return self._get_empty_stats()

    def _process_call_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw call data into statistics."""
        calls = data.get("calls", [])
        
        total = len(calls)
        incoming = 0
        outgoing = 0
        missed = 0
        durations = []
        
        for call in calls:
            call_type = call.get("type", "").lower()
            duration = call.get("duration", 0)
            
            if "incoming" in call_type or "inbound" in call_type:
                incoming += 1
            elif "outgoing" in call_type or "outbound" in call_type:
                outgoing += 1
            elif "missed" in call_type:
                missed += 1
            
            if duration and duration > 0:
                durations.append(duration)
        
        return {
            "total": total,
            "incoming": incoming,
            "outgoing": outgoing,
            "missed": missed,
            "durations": durations,
            "average_duration": sum(durations) / len(durations) if durations else 0,
        }

    def _get_empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics structure."""
        return {
            "total": 0,
            "incoming": 0,
            "outgoing": 0,
            "missed": 0,
            "durations": [],
            "average_duration": 0,
        }

    async def async_cleanup(self) -> None:
        """Clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close() 