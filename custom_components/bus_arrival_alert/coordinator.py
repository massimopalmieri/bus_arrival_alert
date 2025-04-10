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
        self.latest_data = {}

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
        for stop in self.stops:
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

            arrivals = []

            for bus in data:
                if line_names and bus["lineName"] not in line_names:
                    continue

                arrivals.append({
                    "line": bus["lineName"],
                    "station": bus["stationName"],
                    "destination": bus["destinationName"],
                    "minutes": bus["timeToStation"] // 60
                })

            self.latest_data[stop_id] = arrivals

            if arrivals:
                arrivals.sort(key=lambda x: x["minutes"])

                _LOGGER.info("Buses arriving at stop %s: %s", stop_id, arrivals)

                self.hass.bus.async_fire(
                    "bus_arrival_alert",
                    {
                        "stop_id": stop_id,
                        "arrivals": arrivals
                    }
                )