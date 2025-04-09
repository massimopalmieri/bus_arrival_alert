"""Coordinator to handle fetching bus arrivals and firing grouped events."""
import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class BusArrivalManager:
    """Manage fetching bus arrivals and firing grouped events."""

    def __init__(self, hass: HomeAssistant, stops: list[dict], scan_interval: int):
        self.hass = hass
        self.stops = stops
        self.scan_interval = scan_interval
        self.session = aiohttp.ClientSession()
        self._unsub_timer = None

    async def async_start(self):
        """Start the periodic fetching task."""
        if self._unsub_timer:
            self._unsub_timer()

        self._unsub_timer = async_track_time_interval(
            self.hass, self._async_fetch, timedelta(seconds=self.scan_interval)
        )
        _LOGGER.debug("Bus Arrival Manager started with interval %s seconds", self.scan_interval)

    async def async_stop(self):
        """Close the aiohttp session cleanly."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

        await self.session.close()
        _LOGGER.debug("Bus Arrival Manager stopped")

    async def add_stop(self, stop_data: dict):
        """Add a stop dynamically."""
        self.stops.append(stop_data)

    async def remove_stop(self, stop_data: dict):
        """Remove a stop dynamically."""
        self.stops.remove(stop_data)

    async def _async_fetch(self, now):
        """Fetch data and fire grouped events."""
        now_time = datetime.now().time()
        today = datetime.now().strftime("%A").lower()

        for stop in self.stops:
            # Parse start and end time if needed
            start_time = stop["start_time"]
            end_time = stop["end_time"]

            if isinstance(start_time, str):
                start_time = datetime.strptime(start_time, "%H:%M").time()
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, "%H:%M").time()

            stop_days = stop.get("days")
            if stop_days and today not in stop_days:
                continue

            if not (start_time <= now_time <= end_time):
                continue

            stop_id = stop["stop_id"]
            line_names = stop.get("line_names")

            url = f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals"

            try:
                async with async_timeout.timeout(10):
                    async with self.session.get(url) as response:
                        if response.status != 200:
                            _LOGGER.error("Error fetching data for stop %s: HTTP %s", stop_id, response.status)
                            continue

                        data = await response.json()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Exception fetching data for stop %s: %s", stop_id, str(e))
                continue

            arrivals = {}

            for bus in data:
                if line_names and bus["lineName"] not in line_names:
                    continue

                minutes_to_arrival = bus["timeToStation"] // 60
                bus_line = bus["lineName"]
                arrivals.setdefault(bus_line, []).append(minutes_to_arrival)

            if arrivals:
                for bus_line in arrivals:
                    arrivals[bus_line].sort()

                _LOGGER.info("Buses arriving at stop %s: %s", stop_id, arrivals)

                self.hass.bus.async_fire(
                    "bus_arrival_alert",
                    {
                        "stop_id": stop_id,
                        "arrivals": arrivals
                    }
                )