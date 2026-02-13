import json
import logging
import time
from datetime import datetime
from homeassistant.components.mqtt import async_subscribe
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DOMAIN = "sleep_mqtt"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors based on a config_entry."""
    topic = config_entry.data['topic_prefix'].rstrip('/') + "/#"
    device_name = config_entry.data['device_name']
    unique_dev_id = config_entry.entry_id
    
    sys_lang = hass.config.language if hasattr(hass.config, 'language') else 'en'
    lang = 'nl' if sys_lang == 'nl' else 'en'
    
    sensor_list = [
        {"id": "event", "en": "Status", "nl": "Status", "u": None, "i": "mdi:bed"},
        {"id": "start_time_display", "en": "Start Time", "nl": "Starttijd", "u": None, "i": "mdi:clock-start"},
        {"id": "stop_time_display", "en": "End Time", "nl": "Eindtijd", "u": None, "i": "mdi:clock-end"},
        {"id": "alarm_time_display", "en": "Alarm Time", "nl": "Wekker Tijd", "u": None, "i": "mdi:alarm"},
        {"id": "combined_duration", "en": "Sleep Duration", "nl": "Slaap Duur", "u": None, "i": "mdi:timer-sand"},
        {"id": "efficiency", "en": "Sleep Efficiency", "nl": "Slaap Efficiëntie", "u": "%", "i": "mdi:leaf"},
        {"id": "deep_sleep_percentage", "en": "Deep Sleep", "nl": "Diepe Slaap", "u": "%", "i": "mdi:waves", "p": "deep_sleep"},
        {"id": "light_sleep_percentage", "en": "Light Sleep", "nl": "Lichte Slaap", "u": "%", "i": "mdi:circle-slice-4", "p": "light_sleep"},
        {"id": "rem_sleep_percentage", "en": "REM Sleep", "nl": "REM Slaap", "u": "%", "i": "mdi:eye-check", "p": "rem_sleep"},
        {"id": "awake_percentage", "en": "Awake", "nl": "Wakker", "u": "%", "i": "mdi:clock-outline", "p": "awake"},
        {"id": "sound_event_snore", "en": "Snoring", "nl": "Snurken", "u": "times", "nl_u": "keer", "i": "mdi:reproduction", "t": True},
        {"id": "sound_event_talk", "en": "Talking", "nl": "Praten", "u": "times", "nl_u": "keer", "i": "mdi:account-voice", "t": True},
        {"id": "sound_event_cough", "en": "Coughing", "nl": "Hoesten", "u": "times", "nl_u": "keer", "i": "mdi:alert-decagram", "t": True},
        {"id": "sound_event_laugh", "en": "Laughing", "nl": "Lachen", "u": "times", "nl_u": "keer", "i": "mdi:emoticon-happy", "t": True},
        {"id": "sound_event_yawn", "en": "Yawning", "nl": "Gapen", "u": "times", "nl_u": "keer", "i": "mdi:sleep", "t": True},
        {"id": "sound_event_sniff", "en": "Sniffling", "nl": "Snuiten", "u": "times", "nl_u": "keer", "i": "mdi:fountain-pen-tip", "t": True},
        {"id": "last_sync", "en": "Last Sync", "nl": "Laatste Update", "u": None, "i": "mdi:sync"}
    ]
    
    tracker = SleepTracker(lang)
    entities = [SleepSensor(tracker, device_name, s, lang, unique_dev_id) for s in sensor_list]
    async_add_entities(entities)

    async def global_msg_recv(msg):
        try:
            data = json.loads(msg.payload)
            event = data.get("event")
            if not event: return
            tracker.process_event(event)
            for entity in entities:
                entity.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Error processing SleepAsAndroid MQTT message: %s", e)

    await async_subscribe(hass, topic, global_msg_recv)

class SleepTracker:
    def __init__(self, lang):
        self.lang = lang
        self.reset()

    def reset(self):
        self.unix_start = None
        self.unix_stop = None
        self.last_event_time = None
        self.current_phase = "awake"
        self.is_tracking = False
        self.totals = {"deep_sleep": 0, "light_sleep": 0, "rem_sleep": 0, "awake": 0}
        self.counts = {
            "sound_event_snore": 0, "sound_event_talk": 0, "sound_event_cough": 0, 
            "sound_event_laugh": 0, "sound_event_yawn": 0, "sound_event_sniff": 0
        }
        not_yet = "Nog niet" if self.lang == 'nl' else "Not yet"
        self.count_times = {k: not_yet for k in self.counts.keys()}
        self.last_event = "Geen data" if self.lang == 'nl' else "No data"
        self.start_time_str = "Niet gestart" if self.lang == 'nl' else "Not started"
        self.stop_time_str = "Niet gestopt" if self.lang == 'nl' else "Not stopped"
        self.alarm_time_str = "Nog niet afgegaan" if self.lang == 'nl' else "Not triggered"
        self.last_sync_str = "Nooit" if self.lang == 'nl' else "Never"

    def process_event(self, event):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_sync_str = timestamp
        
        if event == "sleep_tracking_started":
            self.reset()
            self.is_tracking = True
            self.unix_start = time.time()
            self.last_event_time = self.unix_start
            self.start_time_str = timestamp
            self.last_event = event
            return

        if self.is_tracking:
            now = time.time()
            if self.last_event_time:
                duration = now - self.last_event_time
                if self.current_phase in self.totals:
                    self.totals[self.current_phase] += duration
            self.last_event_time = now

        if event == "sleep_tracking_stopped":
            self.is_tracking = False
            self.unix_stop = time.time()
            self.stop_time_str = timestamp
            self.current_phase = None
        elif event == "alarm_alert_start":
            self.alarm_time_str = timestamp
        elif event in ["deep_sleep", "light_sleep", "rem_sleep", "awake"]:
            self.current_phase = event
        elif event in self.counts:
            self.counts[event] += 1
            self.count_times[event] = timestamp
        
        self.last_event = event

class SleepSensor(Entity):
    def __init__(self, tracker, device_name, s, lang, unique_dev_id):
        self._tracker, self._id, self._lang = tracker, s["id"], lang
        self._unique_dev_id = unique_dev_id
        self._device_display_name = device_name
        friendly_name = s["nl"] if lang == 'nl' else s["en"]
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unit_of_measurement = s["nl_u"] if lang == 'nl' and "nl_u" in s else s.get("u")
        self._attr_icon = s["i"]
        self._attr_unique_id = f"sleep_custom_{unique_dev_id}_{s['id']}"
        self._phase_key = s.get("p")
        self._is_counter = s.get("t", False)
        self._extra_attrs = {}

    @property
    def extra_state_attributes(self): return self._extra_attrs

    @property
    def state(self):
        if self._id == "event": return self._tracker.last_event
        if self._id == "start_time_display": return self._tracker.start_time_str
        if self._id == "stop_time_display": return self._tracker.stop_time_str
        if self._id == "alarm_time_display": return self._tracker.alarm_time_str
        if self._id == "last_sync": return self._tracker.last_sync_str
        
        if self._tracker.unix_start is None:
            if self._id == "combined_duration": 
                suffix_h = "u" if self._lang == 'nl' else "h"
                return f"0{suffix_h} 0m"
            if self._phase_key or self._id == "efficiency": return 0
            if self._is_counter: return 0
            return None

        end = self._tracker.unix_stop if self._tracker.unix_stop else time.time()
        total_sec = end - self._tracker.unix_start
        
        if self._id == "combined_duration":
            h, m = int(total_sec // 3600), int((total_sec % 3600) // 60)
            attr_key = "decimaal" if self._lang == 'nl' else "decimal"
            self._extra_attrs = {attr_key: round(total_sec / 3600, 2)}
            suffix_h = "u" if self._lang == 'nl' else "h"
            return f"{h}{suffix_h} {m}m"

        if self._id == "efficiency":
            awake_t = self._tracker.totals.get("awake", 0)
            if self._tracker.is_tracking and self._tracker.current_phase == "awake":
                awake_t += (time.time() - self._tracker.last_event_time)
            sleep_t = total_sec - awake_t
            return round((sleep_t / total_sec) * 100, 1) if total_sec > 0 else 0

        if self._is_counter:
            attr_key = "laatst_gedetecteerd" if self._lang == 'nl' else "last_detected"
            self._extra_attrs = {attr_key: self._tracker.count_times.get(self._id)}
            return self._tracker.counts.get(self._id, 0)
        
        if self._phase_key:
            phase_time = self._tracker.totals.get(self._phase_key, 0)
            if self._tracker.is_tracking and self._tracker.current_phase == self._phase_key:
                phase_time += (time.time() - self._tracker.last_event_time)
            
            perc = round((phase_time / total_sec) * 100, 1) if total_sec > 0 else 0
            h, m = int(phase_time // 3600), int((phase_time % 3600) // 60)
            suffix_h = "u" if self._lang == 'nl' else "h"
            time_str = f"{h}{suffix_h} {m}m" if h > 0 else f"{m}m"
            
            attr_time = "tijd_geformatteerd" if self._lang == 'nl' else "time_formatted"
            attr_sec = "tijd_seconden" if self._lang == 'nl' else "time_seconds"
            self._extra_attrs = {attr_time: time_str, attr_sec: round(phase_time)}
            return perc
        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_dev_id)},
            "name": f"SleepAsAndroid MQTT Custom ({self._device_display_name})"
        }
