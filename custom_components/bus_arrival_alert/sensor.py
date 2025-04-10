"""Sensor platform for Bus Arrival Alert."""
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors from a config entry."""
    import logging
    _LOGGER = logging.getLogger(__name__)

    manager = hass.data[DOMAIN]
    entities = []

    _LOGGER.info(f"manager.stops at sensor setup: {manager.stops}")

    if not manager.stops:
        _LOGGER.warning("No stops configured — no sensors will be created.")

    for stop in manager.stops:
        stop_id = stop["stop_id"]
        name = stop.get("name") or stop_id
        _LOGGER.info(f"Creating sensor for stop_id: {stop_id} (name: {name})")
        entities.append(BusArrivalSensor(manager, stop_id, name))

    async_add_entities(entities, update_before_add=True)

class BusArrivalSensor(Entity):
    """Representation of a Bus Arrival sensor."""

    def __init__(self, manager, stop_id, name):
        """Initialize the sensor."""
        self.manager = manager
        self.stop_id = stop_id
        self._attr_name = f"Bus Arrival {name} - {stop_id}"
        self._attr_unique_id = f"bus_arrival_{stop_id.lower()}"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None

    @property
    def native_value(self):
        """Return the state."""
        arrivals = self.manager.latest_data.get(self.stop_id, [])
        if arrivals:
            return f"{len(arrivals)} buses"
        else:
            return "No buses"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        arrivals = self.manager.latest_data.get(self.stop_id, [])
        return {
            "arrivals": arrivals,
            "friendly_name": self._attr_name,
        }