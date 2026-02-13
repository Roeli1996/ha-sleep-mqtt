import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

DOMAIN = "sleep_mqtt"

class SleepMQTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SleepAsAndroid MQTT Custom."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step when adding via UI."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"SleepAsAndroid ({user_input['device_name']})", 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_name", default="Arne"): cv.string,
                vol.Required("topic_prefix", default="SleepAsAndroid/Arne"): cv.string,
            }),
            errors=errors,
        )
