"""Custom component for monitoring bus arrivals and firing alerts."""
import asyncio
from datetime import datetime, time as dt_time
import logging

import aiohttp
import async_timeout

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_PLATFORM, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# Config schema
STOP_SCHEMA = vol.Schema({
    vol.Required("stop_id"): cv.string,
    vol.Optional("line_name"): cv.string,
    vol.Required("start_time"): cv.time,
    vol.Required("end_time"): cv.time,
    vol.Required("threshold_minutes"): vol.All(vol.Coerce(int), vol.Range(min=1))
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        vol.Required("stops"): vol.All(cv.ensure_list, [STOP_SCHEMA])
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Bus Arrival Alert component."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    scan_interval = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    stops = conf["stops"]

    manager = BusArrivalManager(hass, stops, scan_interval)
    hass.data[DOMAIN] = manager

    await manager.async_start()

    return True

class BusArrivalManager:
    def __init__(self, hass: HomeAssistant, stops: list[dict], scan_interval: int):
        self.hass = hass
        self.stops = stops
        self.scan_interval = scan_interval
        self.session = aiohttp.ClientSession()

    async def async_start(self):
        """Start periodic fetching."""
        async_track_time_interval(self.hass, self._async_fetch, timedelta(seconds=self.scan_interval))

    async def _async_fetch(self, now):
        """Fetch arrival data and fire events if needed."""
        now_time = datetime.now().time()

        for stop in self.stops:
            # Only fetch if within the stop's monitoring window
            if not (stop["start_time"] <= now_time <= stop["end_time"]):
                continue

            stop_id = stop["stop_id"]
            line_name = stop.get("line_name")
            threshold_minutes = stop["threshold_minutes"]

            url = f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals"

            try:
                async with async_timeout.timeout(10):
                    async with self.session.get(url) as response:
                        if response.status != 200:
                            _LOGGER.error(f"Error fetching data for stop {stop_id}: {response.status}")
                            continue

                        data = await response.json()

            except Exception as e:
                _LOGGER.error(f"Exception fetching data for stop {stop_id}: {e}")
                continue

            # Process buses
            for bus in data:
                if line_name and bus["lineName"] != line_name:
                    continue

                minutes_to_arrival = bus["timeToStation"] // 60
                if minutes_to_arrival <= threshold_minutes:
                    _LOGGER.info(f"Bus {bus['lineName']} arriving in {minutes_to_arrival} minutes at stop {stop_id}")

                    self.hass.bus.async_fire(
                        "bus_arrival_alert",
                        {
                            "stop_id": stop_id,
                            "line_name": bus["lineName"],
                            "destination": bus["destinationName"],
                            "minutes_to_arrival": minutes_to_arrival
                        }
                    )