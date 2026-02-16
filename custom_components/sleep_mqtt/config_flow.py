import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SleepAsAndroidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Custom SleepAsAndroid MQTT Sensors."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step when adding via UI."""
        if user_input is not None:
            # Voorkom dubbele configuraties voor hetzelfde topic
            unique_id = f"{DOMAIN}_{user_input['topic']}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["device_name"], 
                data=user_input
            )

        # Het formulier met standaardwaarden voor Roeli1996
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_name", default="User-slaap"): str,
                vol.Required("topic", default="SleepAsAndroid/User"): str,
            })
        )
