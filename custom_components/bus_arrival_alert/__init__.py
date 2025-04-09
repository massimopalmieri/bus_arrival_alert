"""Bus Arrival Alert initialization."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .coordinator import BusArrivalManager

# Config schema
STOP_SCHEMA = vol.Schema({
    vol.Required("stop_id"): cv.string,
    vol.Optional("line_names"): vol.All(cv.ensure_list, [cv.string]),
    vol.Required("start_time"): cv.time,
    vol.Required("end_time"): cv.time,
    vol.Optional("days"): vol.All(cv.ensure_list, [cv.string]),
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
        ),
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

    async def _shutdown(event):
        await manager.async_stop()

    hass.bus.async_listen_once("homeassistant_stop", _shutdown)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Set up Bus Arrival Alert from a config entry."""
    manager = hass.data.get(DOMAIN)

    if manager is None:
        from .coordinator import BusArrivalManager
        manager = BusArrivalManager(hass, [], DEFAULT_SCAN_INTERVAL)
        hass.data[DOMAIN] = manager
        await manager.async_start()

    # Merge options if available
    stop_data = {**entry.data, **entry.options}
    await manager.add_stop(stop_data)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Unload a config entry."""
    manager = hass.data.get(DOMAIN)
    if manager:
        await manager.remove_stop(entry.data)

    return True