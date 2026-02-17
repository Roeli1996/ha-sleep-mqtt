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
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    topic = config_entry.data["topic"]
    device_name = config_entry.data["device_name"]
    entry_id = config_entry.entry_id
    
    entities = []
    duration_map = {}

    # 1. Duur Sensoren
    duration_stats = [
        {"id": "light_sleep_duration", "icon": "mdi:sleep"},
        {"id": "deep_sleep_duration", "icon": "mdi:sleep-circle"},
        {"id": "rem_sleep_duration", "icon": "mdi:moon-waning-crescent"},
        {"id": "awake_duration", "icon": "mdi:weather-sunny"},
        {"id": "total_sleep_duration", "icon": "mdi:sigma"},
    ]
    for stat in duration_stats:
        s = SleepAsAndroidDurationSensor(config_entry, stat, device_name)
        duration_map[stat["id"]] = s
        entities.append(s)

    # 2. Geluid Tellers
    sound_map = {}
    sound_types = [
        {"id": "snoring_count", "icon": "mdi:account-voice", "event_key": "snore"},
        {"id": "talking_count", "icon": "mdi:comment-text-outline", "event_key": "talk"},
        {"id": "coughing_count", "icon": "mdi:emoticon-sick", "event_key": "cough"},
        {"id": "laughing_count", "icon": "mdi:emoticon-laugh", "event_key": "laugh"},
        {"id": "shouting_count", "icon": "mdi:account-alert", "event_key": "shout"},
    ]
    for snd in sound_types:
        s = SleepAsAndroidSoundSensor(config_entry, snd, device_name)
        sound_map[snd["event_key"]] = s
        entities.append(s)

    # 3. Timestamps
    fell_asleep_s = SleepAsAndroidTimestampSensor(config_entry, {"id": "fell_asleep", "icon": "mdi:bed-clock"}, device_name)
    start_time_s = SleepAsAndroidTimestampSensor(config_entry, {"id": "start_time", "icon": "mdi:clock-start"}, device_name)
    stop_time_s = SleepAsAndroidTimestampSensor(config_entry, {"id": "stop_time", "icon": "mdi:clock-end"}, device_name)
    alarm_time_s = SleepAsAndroidTimestampSensor(config_entry, {"id": "alarm_time", "icon": "mdi:alarm"}, device_name)
    
    entities.extend([fell_asleep_s, start_time_s, stop_time_s, alarm_time_s])

    # 4. Engine
    eff_s = SleepAsAndroidEfficiencySensor(config_entry, device_name, start_time_s, stop_time_s, duration_map["total_sleep_duration"])
    entities.append(eff_s)
    
    entities.append(SleepAsAndroidPhaseSensor(
        topic, config_entry, device_name, 
        fell_asleep_s, start_time_s, stop_time_s, alarm_time_s, duration_map, sound_map, eff_s
    ))
    
    entities.append(SleepAsAndroidLastMessageSensor(topic, config_entry, device_name))
    
    async_add_entities(entities)

class SleepAsAndroidBaseSensor(SensorEntity):
    def __init__(self, config_entry, device_name):
        self._device_name = device_name
        self._entry_id = config_entry.entry_id
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {("sleep_mqtt", self._entry_id)},
            "name": self._device_name,
            "manufacturer": "Urbandroid",
            "model": "SleepAsAndroid MQTT Custom",
        }

class SleepAsAndroidDurationSensor(SleepAsAndroidBaseSensor):
    def __init__(self, config_entry, stat, device_name):
        super().__init__(config_entry, device_name)
        self._attr_translation_key = stat["id"]
        self._attr_unique_id = f"{self._entry_id}_{stat['id']}"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = stat["icon"]
        self._state = 0.0

    @property
    def native_value(self): return round(self._state, 1)

class SleepAsAndroidSoundSensor(SleepAsAndroidBaseSensor):
    def __init__(self, config_entry, snd, device_name):
        super().__init__(config_entry, device_name)
        self._attr_translation_key = snd["id"]
        self._attr_unique_id = f"{self._entry_id}_{snd['id']}"
        self._attr_icon = snd["icon"]
        self._state = 0
        self._last_seen = None
        self._total_duration_sec = 0.0

    @property
    def native_value(self): return self._state

    @property
    def extra_state_attributes(self):
        return {
            "last_seen": self._last_seen,
            "total_duration_minutes": round(self._total_duration_sec / 60, 2)
        }

class SleepAsAndroidTimestampSensor(SleepAsAndroidBaseSensor):
    def __init__(self, config_entry, ts, device_name):
        super().__init__(config_entry, device_name)
        self._attr_translation_key = ts["id"]
        self._attr_unique_id = f"{self._entry_id}_{ts['id']}"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = ts.get("icon")
        self._state = None

    @property
    def native_value(self): return self._state

class SleepAsAndroidEfficiencySensor(SleepAsAndroidBaseSensor):
    def __init__(self, config_entry, device_name, start_sensor, stop_sensor, total_sleep_sensor):
        super().__init__(config_entry, device_name)
        self._attr_translation_key = "efficiency"
        self._attr_unique_id = f"{self._entry_id}_efficiency_calc"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:chart-line"
        self._start_sensor = start_sensor
        self._stop_sensor = stop_sensor
        self._total_sleep_sensor = total_sleep_sensor
        self._state = 0.0

    def update_efficiency(self):
        if self._start_sensor._state and self._total_sleep_sensor._state > 0:
            end_t = self._stop_sensor._state or dt_util.utcnow()
            total_time_bed = (end_t - self._start_sensor._state).total_seconds() / 60
            if total_time_bed > 0:
                calc = (self._total_sleep_sensor._state / total_time_bed) * 100
                self._state = round(min(calc, 100.0), 1)
                self.async_write_ha_state()

    @property
    def native_value(self): return self._state

class SleepAsAndroidPhaseSensor(SleepAsAndroidBaseSensor):
    def __init__(self, topic, config_entry, device_name, fell_asleep, start_t, stop_t, alarm_t, durations, sounds, efficiency):
        super().__init__(config_entry, device_name)
        self._topic = topic
        self._attr_translation_key = "sleep_phase"
        self._attr_unique_id = f"{self._entry_id}_sleep_phase"
        self._fell_asleep_s = fell_asleep
        self._start_s = start_t
        self._stop_s = stop_t
        self._alarm_s = alarm_t
        self._durations = durations
        self._sounds = sounds
        self._eff_s = efficiency
        self._state = "disabled"
        self._last_msg_time = None
        self._current_phase_id = None
        self._active_sound_id = None

    @property
    def extra_state_attributes(self):
        return {"active_timer": self._current_phase_id}

    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                event = str(data.get("event", "")).lower().strip()
                now = dt_util.utcnow()

                # 1. Start / Pause / Resume
                if event in ["sleep_tracking_started", "sleep_tracking_paused", "sleep_tracking_resumed"]:
                    _LOGGER.debug("Tracking event voor %s: %s", self._device_name, event)
                    
                    if event != "sleep_tracking_resumed":
                        if self._last_msg_time:
                            self._update_all_timers(now)
                        
                        self._start_s._state = now
                        self._stop_s._state = None
                        self._fell_asleep_s._state = None
                        for s in self._durations.values():
                            s._state = 0.0
                            s.async_write_ha_state()
                        for s in self._sounds.values():
                            s._state = 0
                            s._last_seen = None
                            s._total_duration_sec = 0.0
                            s.async_write_ha_state()
                    else:
                        self._update_all_timers(now)
                    
                    if event == "sleep_tracking_paused":
                        self._state = "tracking_paused"
                    else:
                        self._state = "tracking"

                    self._last_msg_time = now
                    # Tijdens pauze/start/hervatting telt de tijd als 'wakker'
                    self._current_phase_id = "awake_duration"
                    self._active_sound_id = None

                    self._start_s.async_write_ha_state()
                    self._stop_s.async_write_ha_state()
                    self._fell_asleep_s.async_write_ha_state()
                    self._eff_s.async_write_ha_state()
                    self.async_write_ha_state()
                    return

                # 2. Stop
                if event == "sleep_tracking_stopped":
                    self._update_all_timers(now)
                    self._stop_s._state = now
                    self._state = "disabled"
                    self._current_phase_id = None
                    self._active_sound_id = None
                    self._stop_s.async_write_ha_state()
                    self._eff_s.update_efficiency()
                    self.async_write_ha_state()
                    return

                self._update_all_timers(now)

                # 3. Fell Asleep Check
                is_sleep_event = any(x in event for x in ["light_sleep", "deep_sleep", "rem", "not_awake"])
                if is_sleep_event and self._fell_asleep_s._state is None:
                    self._fell_asleep_s._state = now
                    self._fell_asleep_s.async_write_ha_state()

                # 4. Phase Mapping
                new_phase_id = None
                if "light_sleep" in event: new_phase_id = "light_sleep"
                elif "deep_sleep" in event: new_phase_id = "deep_sleep"
                elif "rem" in event: new_phase_id = "rem_sleep"
                elif "awake" in event: new_phase_id = "awake"
                elif "not_awake" in event: new_phase_id = "light_sleep"

                if new_phase_id:
                    self._current_phase_id = f"{new_phase_id}_duration"
                    self._state = new_phase_id
                    self._active_sound_id = None

                # 5. Sound Events
                for sid, s_ent in self._sounds.items():
                    if sid in event:
                        s_ent._state += 1
                        s_ent._last_seen = now
                        self._active_sound_id = sid
                        s_ent.async_write_ha_state()

                # 6. Alarm logic
                if "alarm" in event:
                    self._alarm_s._state = now
                    self._alarm_s.async_write_ha_state()
                    self._state = "awake"
                    self._current_phase_id = "awake_duration"

                self.async_write_ha_state()
            except Exception as e: _LOGGER.error("MQTT Error: %s", e)

        await async_subscribe(self.hass, self._topic, message_received)

    def _update_all_timers(self, now):
        if not self._last_msg_time:
            self._last_msg_time = now
            return
        diff_sec = (now - self._last_msg_time).total_seconds()
        diff_min = diff_sec / 60
        
        if 0 < diff_min < 600:
            if self._current_phase_id:
                self._durations[self._current_phase_id]._state += diff_min
                if self._current_phase_id != "awake_duration":
                    self._durations["total_sleep_duration"]._state += diff_min
                
                self._durations[self._current_phase_id].async_write_ha_state()
                self._durations["total_sleep_duration"].async_write_ha_state()
            
            if self._active_sound_id:
                for sid, s_ent in self._sounds.items():
                    if sid == self._active_sound_id:
                        s_ent._total_duration_sec += diff_sec
                        s_ent.async_write_ha_state()
                        break
        
        self._last_msg_time = now
        self._eff_s.update_efficiency()

    @property
    def native_value(self): return self._state

class SleepAsAndroidLastMessageSensor(SleepAsAndroidBaseSensor):
    def __init__(self, topic, config_entry, device_name):
        super().__init__(config_entry, device_name)
        self._topic = topic
        self._attr_translation_key = "last_mqtt_message"
        self._attr_unique_id = f"{self._entry_id}_last_mqtt_message"
        self._state = None
    async def async_added_to_hass(self):
        @callback
        def message_received(msg):
            self._state = msg.payload
            self.async_write_ha_state()
        await async_subscribe(self.hass, self._topic, message_received)
    @property
    def native_value(self): return self._state
