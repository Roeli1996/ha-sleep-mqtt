import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SleepAsAndroidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            unique_id = f"{DOMAIN}_{user_input['topic']}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["device_name"], 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_name", default="Slaap Roeli"): str,
                vol.Required("topic", default="SleepAsAndroid/Roeli"): str,
            })
        )
