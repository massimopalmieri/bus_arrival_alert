"""Config flow for Bus Arrival Alert integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (DEFAULT_SCAN_INTERVAL, DOMAIN, MAX_SCAN_INTERVAL,
                    MIN_SCAN_INTERVAL)


class BusArrivalAlertConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bus Arrival Alert."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._stops = []
        self._scan_interval = DEFAULT_SCAN_INTERVAL

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Handle the initial step."""
        return await self.async_step_init(user_input)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Handle the first step of the config flow."""
        errors = {}

        if user_input is not None:
            self._scan_interval = user_input["scan_interval"]
            return await self.async_step_add_stop()

        schema = vol.Schema({
            vol.Required("scan_interval", default=60): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_add_stop(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Handle adding a bus stop."""
        errors = {}

        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []
            
            stop = {
                "name": user_input["name"],
                "stop_id": user_input["stop_id"],
                "line_names": line_names
            }
            
            self._stops.append(stop)
            
            if user_input.get("add_another", False):
                return await self.async_step_add_stop()
            else:
                # Create the entry with all stops
                return self.async_create_entry(
                    title=f"Bus Arrival Alert ({len(self._stops)} stops)",
                    data={
                        "stops": self._stops,
                        "scan_interval": self._scan_interval
                    },
                )

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("stop_id"): str,
            vol.Optional("line_names", default=""): str,
            vol.Required("add_another", default=False): bool,
        })

        return self.async_show_form(
            step_id="add_stop",
            data_schema=schema,
            errors=errors,
            description_placeholders={"num_stops": str(len(self._stops))},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import BusArrivalAlertOptionsFlow
        return BusArrivalAlertOptionsFlow(config_entry)