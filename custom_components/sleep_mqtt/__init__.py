"""The Custom SleepAsAndroid MQTT Sensors integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# We laden alleen het sensor platform
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Custom SleepAsAndroid MQTT Sensors from a config entry."""
    
    # Registreer de platformen (zoals sensor.py)
    # De sensor.py krijgt automatisch toegang tot de entry.data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Sluit de sensoren voor deze specifieke entry (telefoon/gebruiker) netjes af
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
