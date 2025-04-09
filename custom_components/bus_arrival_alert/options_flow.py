"""Options flow for Bus Arrival Alert integration."""
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

class BusArrivalAlertOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Bus Arrival Alert."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []

            return self.async_create_entry(
                title="",
                data={
                    "name": user_input["name"],
                    "stop_id": user_input["stop_id"],
                    "line_names": line_names,
                    "start_time": user_input["start_time"],
                    "end_time": user_input["end_time"],
                    "days": user_input.get("days", [])
                },
            )

        existing = self.config_entry.data

        schema = vol.Schema({
            vol.Required("name", default=existing.get("name", "")): str,
            vol.Required("stop_id", default=existing.get("stop_id", "")): str,
            vol.Optional("line_names", default=",".join(existing.get("line_names", []))): str,
            vol.Required("start_time", default=existing.get("start_time", "")): str,
            vol.Required("end_time", default=existing.get("end_time", "")): str,
            vol.Optional("days", default=existing.get("days", [])): cv.multi_select(DAYS_OF_WEEK),
        })

        return self.async_show_form(step_id="init", data_schema=schema)