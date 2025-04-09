"""Config flow for Bus Arrival Alert integration."""
from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

class BusArrivalAlertConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bus Arrival Alert."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Process line names
            line_names = [line.strip() for line in user_input["line_names"].split(",")] if user_input["line_names"] else []

            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "stop_id": user_input["stop_id"],
                    "line_names": line_names,
                    "start_time": user_input["start_time"],
                    "end_time": user_input["end_time"],
                    "days": user_input.get("days", [])
                },
            )

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("stop_id"): str,
            vol.Optional("line_names", default=""): str,
            vol.Required("start_time"): str,
            vol.Required("end_time"): str,
            vol.Optional("days", default=[]): cv.multi_select(DAYS_OF_WEEK),
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import BusArrivalAlertOptionsFlow
        return BusArrivalAlertOptionsFlow(config_entry)