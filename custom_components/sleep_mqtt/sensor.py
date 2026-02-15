import json
import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime, PERCENTAGE
from homeassistant.core import callback
from homeassistant.components.mqtt import async_subscribe

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SleepAsAndroid MQTT sensors."""
    topic = config_entry.data.get("topic", "SleepAsAndroid/test")
    device_name = config_entry.data.get("device_name", "SleepAsAndroid")
    # We gebruiken de entry_id om elk apparaat uniek te maken in de registry
    entry_id = config_entry.entry_id
    
    entities = []

    # 1. Duur Sensoren
    stats_config = [
        {"id": "light_sleep", "name": "Light Sleep Duration", "icon": "mdi:sleep"},
        {"id": "deep_sleep", "name": "Deep Sleep Duration", "icon": "mdi:sleep-circle"},
        {"id": "rem", "name": "REM Sleep Duration", "icon": "mdi:moon-waning-crescent"},
        {"id": "awake", "name": "Awake Duration", "icon": "mdi:weather-sunny"},
        {"id": "snore", "name": "Snoring Duration", "icon": "mdi:account-voice"},
        {"id": "talk", "name": "Talking Duration", "icon": "mdi:comment-text-outline"},
    ]
    for stat in stats_config:
        entities.append(SleepAsAndroidDurationSensor(hass, config_entry, stat, topic, device_name, entry_id))

    # 2. Totaal en Efficiëntie
    entities.append(SleepAsAndroidTotalSleepSensor(hass, config_entry, topic, device_name, entry_id))
    entities.append(SleepAsAndroidEfficiencySensor(hass, config_entry, topic, device_name, entry_id))
    
    # 3. Tijdstip Sensoren
    time_sensors = [
        {"id": "start_time_display", "name": "Start Time", "icon": "mdi:clock-start"},
        {"id": "fell_asleep_time", "name": "Fell Asleep", "icon": "mdi:bed-clock"},
        {"id": "stop_time_display", "name": "End Time", "icon": "mdi:clock-end"},
        {"id": "alarm_time_display", "name": "Alarm Time", "icon": "mdi:alarm"},
    ]
    for ts in time_sensors:
        entities.append(SleepAsAndroidTimeSensor(hass, config_entry, ts, topic, device_name, entry_id))
    
    # 4. Fase Sensor
    entities.append(SleepAsAndroidPhaseSensor(hass, config_entry, topic, device_name, entry_id))
    
    async_add_entities(entities)

class SleepAsAndroidBaseSensor(SensorEntity):
    """Base class met unieke device identificatie per config entry."""
    def __init__(self, config_entry, topic, device_name, entry_id):
        self._topic = topic
        self._device_name = device_name
        self._entry_id = entry_id

    @property
    def device_info(self):
        # Door de entry_id hier te gebruiken, MOET HA er een apart apparaat van maken
        return {
            "identifiers": {("sleep_mqtt", self._entry_id)},
            "name": self._device_name,
            "manufacturer": "Urbandroid",
            "model": "SleepAsAndroid Custom",
        }

class SleepAsAndroidDurationSensor(SleepAsAndroidBaseSensor):
    def __init__(self, hass, config_entry, stat, topic, device_name, entry_id):
        super().__init__(config_entry, topic, device_name, entry_id)
        self._stat_id = stat["id"]
        self._attr_name = f"{device_name} {stat['name']}"
        self._attr_unique_id = f"{entry_id}_{stat['id']}"
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
            except (json.JSONDecodeError, ValueError): pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self): return self._state

    @property
    def extra_state_attributes(self):
        pct = 0.0
        if self._total_time > 0:
            pct = round((self._state / self._total_time) * 100, 1)
        return {"percentage_of_total": f"{pct}%"}

class SleepAsAndroidTimeSensor(SleepAsAndroidBaseSensor):
    def __init__(self, hass, config_entry, ts, topic, device_name, entry_id):
        super().__init__(config_entry, topic, device_name, entry_id)
        self._ts_id = ts["id"]
        self._attr_name = f"{device_name} {ts['name']}"
        self._attr_unique_id = f"{entry_id}_{ts['id']}"
        self._state = "Unknown"
        self._attr_icon = ts["icon"]

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                if self._ts_id in data:
                    self._state = str(data[self._ts_id])
                    self.async_write_ha_state()
            except (json.JSONDecodeError, ValueError): pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self): return self._state

class SleepAsAndroidEfficiencySensor(SleepAsAndroidBaseSensor):
    def __init__(self, hass, config_entry, topic, device_name, entry_id):
        super().__init__(config_entry, topic, device_name, entry_id)
        self._attr_name = f"{device_name} Efficiency"
        self._attr_unique_id = f"{entry_id}_efficiency"
        self._state = 0.0
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:chart-donut"

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                if "efficiency" in data:
                    self._state = float(data["efficiency"]) * 100
                    self.async_write_ha_state()
            except (json.JSONDecodeError, ValueError): pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self): return self._state

class SleepAsAndroidTotalSleepSensor(SleepAsAndroidBaseSensor):
    def __init__(self, hass, config_entry, topic, device_name, entry_id):
        super().__init__(config_entry, topic, device_name, entry_id)
        self._attr_name = f"{device_name} Total Sleep"
        self._attr_unique_id = f"{entry_id}_total_sleep"
        self._state = 0.0
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
            except (json.JSONDecodeError, ValueError): pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self): return self._state

class SleepAsAndroidPhaseSensor(SleepAsAndroidBaseSensor):
    def __init__(self, hass, config_entry, topic, device_name, entry_id):
        super().__init__(config_entry, topic, device_name, entry_id)
        self._attr_name = f"{device_name} Sleep Phase"
        self._attr_unique_id = f"{entry_id}_sleep_phase"
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
            except (json.JSONDecodeError, ValueError): pass
        await async_subscribe(self.hass, self._topic, message_received)

    @property
    def native_value(self): return self._state
