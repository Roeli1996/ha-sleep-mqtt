import json
import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import callback
from homeassistant.components.mqtt import async_subscribe

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SleepAsAndroid MQTT sensors."""
    topic = config_entry.data.get("topic", "SleepAsAndroid/test")
    
    # Configuratie van duur-sensoren (Zonder Noise)
    stats_config = [
        {"id": "light_sleep", "name": "Light Sleep", "icon": "mdi:sleep"},
        {"id": "deep_sleep", "name": "Deep Sleep", "icon": "mdi:sleep-circle"},
        {"id": "rem", "name": "REM Sleep", "icon": "mdi:moon-waning-crescent"},
        {"id": "awake", "name": "Awake", "icon": "mdi:weather-sunny"},
        {"id": "snore", "name": "Snoring Duration", "icon": "mdi:account-voice"},
        {"id": "talk", "name": "Talking Duration", "icon": "mdi:comment-text-outline"},
    ]
    
    entities = [SleepAsAndroidDurationSensor(hass, config_entry, stat, topic) for stat in stats_config]
    entities.append(SleepAsAndroidTotalSleepSensor(hass, config_entry, topic))
    entities.append(SleepAsAndroidPhaseSensor(hass, config_entry, topic))
    
    async_add_entities(entities)

class SleepAsAndroidDurationSensor(SensorEntity):
    """Sensor voor duur per fase/geluid met percentage-attribuut."""

    def __init__(self, hass, config_entry, stat, topic):
        self._stat_id = stat["id"]
        self._attr_name = f"SleepAsAndroid {stat['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{stat['id']}"
        self._topic = topic
        self._state = 0.0
        self._total_time = 0.0
        self._attr_icon = stat["icon"]
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                self._total_time = float(data.get("total", 0.0))
                if self._stat_id in data:
                    self._state = float(data[self._stat_id])
                    self.async_write_ha_state()
            except (json.JSONDecodeError, ValueError):
                pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        pct = 0.0
        if self._total_time > 0:
            pct = round((self._state / self._total_time) * 100, 1)
        return {"percentage_of_total": f"{pct}%"}

    @property
    def device_info(self):
        return {"identifiers": {("sleep_mqtt", self._topic)}, "name": "SleepAsAndroid MQTT Custom"}

class SleepAsAndroidTotalSleepSensor(SensorEntity):
    """Sensor voor de totale slaapduur."""

    def __init__(self, hass, config_entry, topic):
        self._attr_name = "SleepAsAndroid Total Sleep"
        self._attr_unique_id = f"{config_entry.entry_id}_total_sleep"
        self._topic = topic
        self._state = 0.0
        self._attr_icon = "mdi:timer-outline"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                if "total" in data:
                    self._state = float(data["total"])
                    self.async_write_ha_state()
            except (json.JSONDecodeError, ValueError):
                pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        return {"identifiers": {("sleep_mqtt", self._topic)}, "name": "SleepAsAndroid MQTT Custom"}

class SleepAsAndroidPhaseSensor(SensorEntity):
    """Tekst-sensor die de fase onthoudt tijdens geluidsevents."""

    def __init__(self, hass, config_entry, topic):
        self._attr_name = "SleepAsAndroid Sleep Phase"
        self._attr_unique_id = f"{config_entry.entry_id}_sleep_phase"
        self._topic = topic
        self._state = "Unknown"
        self._last_phase = "Unknown"
        self._attr_icon = "mdi:bed"

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                event = data.get("event", "").lower()
                
                new_p = None
                if "rem" in event: new_p = "REM"
                elif "deep" in event: new_p = "Deep Sleep"
                elif "light" in event: new_p = "Light Sleep"
                elif "awake" in event: new_p = "Awake"

                if new_p:
                    self._last_phase = new_p
                    self._state = new_p

                if "snore" in event:
                    self._state = f"{self._last_phase} (Snoring)"
                    self._attr_icon = "mdi:account-voice"
                elif "talk" in event:
                    self._state = f"{self._last_phase} (Talking)"
                    self._attr_icon = "mdi:comment-text-outline"

                self.async_write_ha_state()
            except (json.JSONDecodeError, ValueError):
                pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        return {"identifiers": {("sleep_mqtt", self._topic)}, "name": "SleepAsAndroid MQTT Custom"}
