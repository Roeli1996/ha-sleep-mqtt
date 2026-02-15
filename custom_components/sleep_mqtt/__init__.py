"""The Custom SleepAsAndroid MQTT Sensors integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# We ondersteunen alleen sensoren
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SleepAsAndroid MQTT Custom from a config entry."""
    # Sla de configuratie op in hass.data zodat elke entry (persoon) zijn eigen data heeft
    hass.data.setdefault("sleep_mqtt", {})
    hass.data["sleep_mqtt"][entry.entry_id] = entry.data

    # Start de sensor-platformen voor deze specifieke entry
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Probeer de sensor-platformen netjes af te sluiten voor deze persoon
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Verwijder de data van deze specifieke persoon uit het geheugen
        hass.data["sleep_mqtt"].pop(entry.entry_id)

    return unload_ok
