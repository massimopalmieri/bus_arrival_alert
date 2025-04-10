"""The Bus Arrival Alert integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import BusArrivalManager

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bus Arrival Alert from a config entry."""
    data = entry.options if entry.options else entry.data

    stop_configs = data.get("stops", [])
    scan_interval = data.get("scan_interval", 120)

    manager = BusArrivalManager(hass, stop_configs, scan_interval)
    hass.data[DOMAIN] = manager
    await manager.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Setup listener for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        manager = hass.data.get(DOMAIN)
        if manager:
            await manager.async_stop()
            hass.data.pop(DOMAIN, None)

    return unload_ok