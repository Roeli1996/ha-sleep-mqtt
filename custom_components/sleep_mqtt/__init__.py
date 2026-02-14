import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "sleep_mqtt"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the integration for a specific config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Sla de configuratie op per entry_id
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Start het sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok
