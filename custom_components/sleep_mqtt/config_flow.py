import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

# Gebruik exact hetzelfde domein als in je manifest
DOMAIN = "sleep_mqtt"

class SleepAsAndroidMQTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SleepAsAndroid MQTT Custom."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step when adding via UI."""
        errors = {}

        if user_input is not None:
            # We maken een uniek ID op basis van het topic. 
            # Dit zorgt ervoor dat je niet twee keer exact hetzelfde topic kunt toevoegen,
            # maar wel verschillende personen (verschillende topics).
            unique_id = f"{DOMAIN}_{user_input['topic']}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["device_name"], 
                data={
                    "device_name": user_input["device_name"],
                    "topic": user_input["topic"]
                }
            )

        # Het formulier dat de gebruiker te zien krijgt
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_name", default="Arne"): str,
                vol.Required("topic", default="SleepAsAndroid/Arne"): str,
            }),
            errors=errors,
        )
