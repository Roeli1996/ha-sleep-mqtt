import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "sleep_mqtt"

async def async_setup_entry(hass, entry):
    """Setup the integration for a specific config entry."""
    hass.data.setdefault(DOMAIN, {})
    # Store config per entry_id to support multiple devices
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
