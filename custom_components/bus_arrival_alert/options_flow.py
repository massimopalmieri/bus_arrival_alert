"""Options flow for Bus Arrival Alert integration."""
import voluptuous as vol
from homeassistant import config_entries

class BusArrivalAlertOptionsFlow(config_entries.OptionsFlowWithConfigEntry):
    """Handle options for Bus Arrival Alert."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []

            # Start from the existing config
            options = dict(self.config_entry.data)

            # Update only what changed
            options["stops"] = [
                {
                    "name": user_input["name"],
                    "stop_id": user_input["stop_id"],
                    "line_names": line_names
                }
            ]
            options["scan_interval"] = user_input.get("scan_interval", 60)

            return self.async_create_entry(
                title="",
                data=options,
            )

        existing_stops = self.config_entry.data.get("stops", [])
        first_stop = existing_stops[0] if existing_stops else {}

        schema = vol.Schema({
            vol.Required("name", default=first_stop.get("name", "")): str,
            vol.Required("stop_id", default=first_stop.get("stop_id", "")): str,
            vol.Optional("line_names", default=",".join(first_stop.get("line_names", []))): str,
            vol.Optional("scan_interval", default=self.config_entry.data.get("scan_interval", 60)): vol.All(int, vol.Range(min=30, max=600)),
        })

        return self.async_show_form(step_id="init", data_schema=schema)