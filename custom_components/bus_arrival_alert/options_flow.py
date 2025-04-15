"""Options flow for Bus Arrival Alert integration."""
import voluptuous as vol
from homeassistant import config_entries

from .const import DEFAULT_SCAN_INTERVAL, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL


class BusArrivalAlertOptionsFlow(config_entries.OptionsFlowWithConfigEntry):
    """Handle options for Bus Arrival Alert."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__(config_entry)
        # Get the latest config - use options if available, otherwise use data
        if self.config_entry.options:
            config = self.config_entry.options
        else:
            config = self.config_entry.data

        self.stops = list(config.get("stops", []))
        self.scan_interval = config.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        self.current_stop_index = None

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.scan_interval = user_input["scan_interval"]
            return await self.async_step_stop_menu()

        schema = vol.Schema({
            vol.Required("scan_interval", default=self.scan_interval): 
                vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        })

        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_stop_menu(self, user_input=None):
        """Show menu for stop management."""
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_add_stop()
            elif user_input["action"] == "edit":
                return await self.async_step_select_stop()
            elif user_input["action"] == "remove":
                return await self.async_step_remove_stop()
            elif user_input["action"] == "done":
                # Return updated options
                return self.async_create_entry(
                    title="",
                    data={
                        "stops": self.stops,
                        "scan_interval": self.scan_interval
                    },
                )

        schema = vol.Schema({
            vol.Required("action"): vol.In({
                "add": "Add a new stop",
                "edit": "Edit existing stop",
                "remove": "Remove a stop",
                "done": "Save and exit"
            }),
        })

        return self.async_show_form(
            step_id="stop_menu",
            data_schema=schema,
            description_placeholders={"num_stops": str(len(self.stops))},
        )

    async def async_step_add_stop(self, user_input=None):
        """Add a bus stop."""
        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []
            
            stop = {
                "name": user_input["name"],
                "stop_id": user_input["stop_id"],
                "line_names": line_names
            }
            
            self.stops.append(stop)
            return await self.async_step_stop_menu()

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("stop_id"): str,
            vol.Optional("line_names", default=""): str,
        })

        return self.async_show_form(step_id="add_stop", data_schema=schema)

    async def async_step_select_stop(self, user_input=None):
        """Select a stop to edit."""
        if not self.stops:
            return await self.async_step_stop_menu()

        if user_input is not None:
            self.current_stop_index = int(user_input["stop_index"])
            return await self.async_step_edit_stop()

        stop_names = {str(i): f"{stop['name']} ({stop['stop_id']})" 
                      for i, stop in enumerate(self.stops)}

        schema = vol.Schema({
            vol.Required("stop_index"): vol.In(stop_names),
        })

        return self.async_show_form(step_id="select_stop", data_schema=schema)

    async def async_step_edit_stop(self, user_input=None):
        """Edit a selected stop."""
        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []
            
            self.stops[self.current_stop_index] = {
                "name": user_input["name"],
                "stop_id": user_input["stop_id"],
                "line_names": line_names
            }
            
            return await self.async_step_stop_menu()

        current_stop = self.stops[self.current_stop_index]
        
        schema = vol.Schema({
            vol.Required("name", default=current_stop["name"]): str,
            vol.Required("stop_id", default=current_stop["stop_id"]): str,
            vol.Optional("line_names", default=",".join(current_stop.get("line_names", []))): str,
        })

        return self.async_show_form(step_id="edit_stop", data_schema=schema)

    async def async_step_remove_stop(self, user_input=None):
        """Remove a stop."""
        if not self.stops:
            return await self.async_step_stop_menu()

        if user_input is not None:
            self.stops.pop(int(user_input["stop_index"]))
            return await self.async_step_stop_menu()

        stop_names = {str(i): f"{stop['name']} ({stop['stop_id']})" 
                      for i, stop in enumerate(self.stops)}

        schema = vol.Schema({
            vol.Required("stop_index"): vol.In(stop_names),
        })

        return self.async_show_form(step_id="remove_stop", data_schema=schema)