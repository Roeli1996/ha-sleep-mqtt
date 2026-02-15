"""The Custom SleepAsAndroid MQTT Sensors integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# We definiëren welke platformen we moeten laden (alleen sensor in dit geval)
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SleepAsAndroid MQTT Custom from a config entry."""
    
    # Maak een centrale opslagplek voor de data als deze nog niet bestaat
    hass.data.setdefault("sleep_mqtt", {})
    
    # Sla de configuratie van deze specifieke persoon op onder zijn eigen entry_id
    # Dit voorkomt dat Persoon A en Persoon B elkaars data overschrijven
    hass.data["sleep_mqtt"][entry.entry_id] = entry.data

    # Registreer de platformen (zoals sensor.py) voor deze entry
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    # Sluit alle sensoren en verbindingen voor deze specifieke persoon netjes af
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Verwijder de data van deze specifieke persoon uit het geheugen van Home Assistant
        if entry.entry_id in hass.data["sleep_mqtt"]:
            hass.data["sleep_mqtt"].pop(entry.entry_id)

    return unload_ok
