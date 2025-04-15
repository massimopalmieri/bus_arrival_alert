"""Sensor platform for Bus Arrival Alert."""
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from a config entry."""
    import logging
    _LOGGER = logging.getLogger(__name__)

    # Support multiple config entries
    manager = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    if not manager.stops:
        _LOGGER.warning("No stops configured — no sensors will be created.")
        return

    # Get stop configs directly from the config entry to ensure proper association
    stop_configs = config_entry.options.get("stops", []) or config_entry.data.get("stops", [])
    
    for stop_config in stop_configs:
        stop_id = stop_config["stop_id"]
        name = stop_config.get("name") or stop_id
        
        # Create a unique_id that includes the config entry ID to ensure proper association
        unique_id = f"{config_entry.entry_id}_{stop_id.lower()}"
        
        _LOGGER.info(f"Creating sensor for stop_id: {stop_id} (name: {name})")
        entities.append(BusArrivalSensor(manager, stop_id, name, unique_id, config_entry.entry_id))

    if entities:
        async_add_entities(entities, update_before_add=True)


class BusArrivalSensor(SensorEntity):
    """Representation of a Bus Arrival sensor."""

    def __init__(self, manager, stop_id, name, unique_id, entry_id):
        """Initialize the sensor."""
        self.manager = manager
        self.stop_id = stop_id
        self._attr_name = f"Bus Arrival {name} - {stop_id}"
        self._attr_unique_id = f"bus_arrival_{unique_id}"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._entry_id = entry_id
        
        # Associate this entity with its config entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": name,
            "manufacturer": "Bus Arrival Alert",
            "model": "Bus Stop",
        }

    @property
    def native_value(self):
        """Return the state."""
        arrivals = self.manager.latest_data.get(self.stop_id)
        if arrivals is None:
            return None  # Data not yet available
        if arrivals:
            return f"{len(arrivals)} buses"
        else:
            return "No buses"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        arrivals = self.manager.latest_data.get(self.stop_id)
        if arrivals is None:
            return {"arrivals": [], "friendly_name": self._attr_name, "status": "Unknown"}
        return {
            "arrivals": arrivals,
            "friendly_name": self._attr_name,
        }