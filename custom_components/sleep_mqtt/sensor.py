import json
import logging
import time
from datetime import datetime

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "sleep_mqtt"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors based on a config_entry."""
    topic = entry.data['topic_prefix'].rstrip('/') + "/#"
    device_name = entry.data['device_name']
    unique_dev_id = entry.entry_id
    
    # Bepaal taal voor interne logs/hardcoded strings
    sys_lang = hass.config.language if hasattr(hass.config, 'language') else 'en'
    lang = 'nl' if sys_lang == 'nl' else 'en'
    
    sensor_list = [
        {"id": "event", "key": "event", "u": None, "i": "mdi:bed"},
        {"id": "sleep_phase", "key": "sleep_phase", "u": "fase", "i": "mdi:chart-timeline-variant", "sc": SensorStateClass.MEASUREMENT},
        {"id": "start_time_display", "key": "start_time_display", "u": None, "i": "mdi:clock-start"},
        {"id": "fell_asleep_time", "key": "fell_asleep_time", "u": None, "i": "mdi:sleep"},
        {"id": "stop_time_display", "key": "stop_time_display", "u": None, "i": "mdi:clock-end"},
        {"id": "alarm_time_display", "key": "alarm_time_display", "u": None, "i": "mdi:alarm"},
        {"id": "combined_duration", "key": "combined_duration", "u": UnitOfTime.HOURS, "i": "mdi:timer-sand", "sc": SensorStateClass.MEASUREMENT},
        {"id": "efficiency", "key": "efficiency", "u": "%", "i": "mdi:leaf", "sc": SensorStateClass.MEASUREMENT},
        {"id": "deep_sleep_percentage", "key": "deep_sleep_percentage", "u": "%", "i": "mdi:waves", "p": "deep_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "light_sleep_percentage", "key": "light_sleep_percentage", "u": "%", "i": "mdi:circle-slice-4", "p": "light_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "rem_sleep_percentage", "key": "rem_sleep_percentage", "u": "%", "i": "mdi:eye-check", "p": "rem_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "awake_percentage", "key": "awake_percentage", "u": "%", "i": "mdi:clock-outline", "p": "awake", "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_snore", "key": "sound_event_snore", "u": "keer", "i": "mdi:reproduction", "t": True, "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_talk", "key": "sound_event_talk", "u": "keer", "i": "mdi:account-voice", "t": True, "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_cough", "key": "sound_event_cough", "u": "keer", "i": "mdi:alert-decagram", "t": True, "sc": SensorStateClass.MEASUREMENT},
        {"id": "last_sync", "key": "last_sync", "u": None, "i": "mdi:sync"}
    ]
    
    tracker = SleepTracker(lang)
    entities = [SleepSensor(tracker, device_name, s, unique_dev_id) for s in sensor_list]
    async_add_entities(entities)

    async def global_msg_recv(msg):
        """Handle incoming MQTT messages."""
        try:
            data = json.loads(msg.payload)
            event = data.get("event")
            if not event:
                return
            tracker.process_event(event)
            for entity in entities:
                entity.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Error processing SleepAsAndroid MQTT message: %s", e)

    # Gebruik de aangeraden mqtt component subscribe
    await mqtt.async_subscribe(hass, topic, global_msg_recv)

class SleepTracker:
    def __init__(self, lang):
        self.lang = lang
        self.reset()

    def reset(self):
        self.unix_start = None
        self.unix_stop = None
        self.last_event_time = None
        self.current_phase_num = 0
        self.current_phase_text = "Standby"
        self.current_phase_key = "awake"
        self.is_tracking = False
        self.fell_asleep_time_str = "Nog niet" if self.lang == 'nl' else "Not yet"
        self.totals = {"deep_sleep": 0, "light_sleep": 0, "rem_sleep": 0, "awake": 0}
        self.counts = {k: 0 for k in ["sound_event_snore", "sound_event_talk", "sound_event_cough"]}
        self.count_times = {k: ("Nog niet" if self.lang == 'nl' else "Not yet") for k in self.counts.keys()}
        self.last_event = "Geen data" if self.lang == 'nl' else "No data"
        self.start_time_str = "Niet gestart" if self.lang == 'nl' else "Not started"
        self.stop_time_str = "Niet gestopt" if self.lang == 'nl' else "Not stopped"
        self.alarm_time_str = "Nog niet afgegaan" if self.lang == 'nl' else "Not triggered"
        self.last_sync_str = "Nooit" if self.lang == 'nl' else "Never"

    def process_event(self, event):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_sync_str = timestamp
        
        if event in ["sleep_tracking_started", "sleep_tracking_paused"]:
            if not self.unix_start:
                self.reset()
                self.unix_start = time.time()
                self.start_time_str = timestamp
            
            self.is_tracking = True
            self.last_event_time = time.time()
            self.current_phase_num = 4
            self.current_phase_key = "awake"
            self.current_phase_text = "Wakker" if self.lang == 'nl' else "Awake"
            self.last_event = event
            return

        if event in ["deep_sleep", "light_sleep", "rem_sleep", "awake"] and not self.unix_start:
            self.reset()
            self.unix_start = time.time()
            self.start_time_str = timestamp + " (Auto)"
            self.is_tracking = True
            self.last_event_time = time.time()

        if self.is_tracking:
            now = time.time()
            if self.last_event_time:
                duration = now - self.last_event_time
                if self.current_phase_key in self.totals:
                    self.totals[self.current_phase_key] += duration
            self.last_event_time = now

        if event == "sleep_tracking_stopped":
            self.is_tracking = False
            self.unix_stop = time.time()
            self.stop_time_str = timestamp
            self.current_phase_num = 0
            self.current_phase_text = "Standby"
        elif event in ["deep_sleep", "light_sleep", "rem_sleep"]:
            if self.fell_asleep_time_str in ["Nog niet", "Not yet"]:
                self.fell_asleep_time_str = timestamp
            
            self.current_phase_key = event
            mapping = {
                "deep_sleep": {"num": 1, "nl": "Diep", "en": "Deep"},
                "light_sleep": {"num": 2, "nl": "Licht", "en": "Light"},
                "rem_sleep": {"num": 3, "nl": "REM", "en": "REM"}
            }
            res = mapping.get(event)
            self.current_phase_num = res["num"]
            self.current_phase_text = res["nl"] if self.lang == 'nl' else res["en"]
        elif event == "awake":
            self.current_phase_key = "awake"
            self.current_phase_num = 4
            self.current_phase_text = "Wakker" if self.lang == 'nl' else "Awake"
        elif event in self.counts:
            self.counts[event] += 1
            self.count_times[event] = timestamp
        
        self.last_event = event

class SleepSensor(SensorEntity):
    def __init__(self, tracker, device_name, s, unique_dev_id):
        self._tracker = tracker
        self._id = s["id"]
        self._device_display_name = device_name
        
        self._attr_translation_key = s["key"]
        self._attr_has_entity_name = True
        
        self._attr_unit_of_measurement = s.get("u")
        self._attr_icon = s["i"]
        self._attr_unique_id = f"sleep_custom_{unique_dev_id}_{s['id']}"
        self._attr_state_class = s.get("sc")
        self._phase_key = s.get("p")
        self._is_counter = s.get("t", False)
        self._extra_attrs = {}

    @property
    def extra_state_attributes(self):
        return self._extra_attrs

    @property
    def native_value(self): # Gebruik native_value voor SensorEntity
        if self._id == "event": return self._tracker.last_event
        if self._id == "start_time_display": return self._tracker.start_time_str
        if self._id == "fell_asleep_time": return self._tracker.fell_asleep_time_str
        if self._id == "stop_time_display": return self._tracker.stop_time_str
        if self._id == "alarm_time_display": return self._tracker.alarm_time_str
        if self._id == "last_sync": return self._tracker.last_sync_str

        if self._id == "sleep_phase":
            self._extra_attrs = {"fase_tekst": self._tracker.current_phase_text}
            return self._tracker.current_phase_num

        if self._tracker.unix_start is None:
            return 0 if (self._phase_key or self._id in ["efficiency", "combined_duration"] or self._is_counter) else None

        end = self._tracker.unix_stop if self._tracker.unix_stop else time.time()
        total_sec = end - self._tracker.unix_start
        
        if self._id == "combined_duration":
            h, m = int(total_sec // 3600), int((total_sec % 3600) // 60)
            display_val = f"{h}u {m}m" if self._tracker.lang == 'nl' else f"{h}h {m}m"
            self._extra_attrs = {"weergave": display_val}
            return round(total_sec / 3600, 2)

        if self._id == "efficiency":
            awake_t = self._tracker.totals.get("awake", 0)
            if self._tracker.is_tracking and self._tracker.current_phase_key == "awake":
                awake_t += (time.time() - self._tracker.last_event_time)
            sleep_t = max(0, total_sec - awake_t)
            return round((sleep_t / total_sec) * 100, 1) if total_sec > 0 else 0

        if self._is_counter:
            attr_key = "laatst_gedetecteerd" if self._tracker.lang == 'nl' else "last_detected"
            self._extra_attrs = {attr_key: self._tracker.count_times.get(self._id)}
            return self._tracker.counts.get(self._id, 0)
        
        if self._phase_key:
            phase_time = self._tracker.totals.get(self._phase_key, 0)
            if self._tracker.is_tracking and self._tracker.current_phase_key == self._phase_key:
                phase_time += (time.time() - self._tracker.last_event_time)
            
            h, m = int(phase_time // 3600), int((phase_time % 3600) // 60)
            display_val = f"{h}u {m}m" if self._tracker.lang == 'nl' else f"{h}h {m}m"
            self._extra_attrs = {"tijd_weergave": display_val}
            return round((phase_time / total_sec) * 100, 1) if total_sec > 0 else 0

        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id.split('_')[2])}, # Gebruik de entry_id voor groepering
            "name": f"Custom SleepAsAndroid MQTT Sensors ({self._device_display_name})",
            "manufacturer": "SleepAsAndroid",
            "model": "MQTT Custom Tracker"
        }
