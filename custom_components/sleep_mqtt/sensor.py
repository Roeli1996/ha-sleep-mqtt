import json
import logging
import time
from datetime import datetime
from homeassistant.components.mqtt import async_subscribe
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTime

_LOGGER = logging.getLogger(__name__)
DOMAIN = "sleep_mqtt"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup sensoren via config_entry."""
    topic = config_entry.data['topic_prefix'].rstrip('/') + "/#"
    device_name = config_entry.data['device_name']
    unique_dev_id = config_entry.entry_id
    
    sys_lang = hass.config.language if hasattr(hass.config, 'language') else 'en'
    lang = 'nl' if sys_lang == 'nl' else 'en'
    
    sensor_list = [
        {"id": "event", "en": "Status", "nl": "Status", "u": None, "i": "mdi:bed"},
        {"id": "sleep_phase", "en": "Sleep Phase", "nl": "Slaapfase", "u": "fase", "i": "mdi:chart-timeline-variant", "sc": SensorStateClass.MEASUREMENT},
        {"id": "start_time_display", "en": "Start Time", "nl": "Starttijd", "u": None, "i": "mdi:clock-start"},
        {"id": "fell_asleep_time", "en": "Fell Asleep", "nl": "In slaap gevallen", "u": None, "i": "mdi:sleep"},
        {"id": "stop_time_display", "en": "End Time", "nl": "Eindtijd", "u": None, "i": "mdi:clock-end"},
        {"id": "alarm_time_display", "en": "Alarm Time", "nl": "Wekker Tijd", "u": None, "i": "mdi:alarm"},
        {"id": "combined_duration", "en": "Sleep Duration", "nl": "Slaap Duur", "u": UnitOfTime.HOURS, "i": "mdi:timer-sand", "sc": SensorStateClass.MEASUREMENT},
        {"id": "efficiency", "en": "Sleep Efficiency", "nl": "Slaap Efficiëntie", "u": "%", "i": "mdi:leaf", "sc": SensorStateClass.MEASUREMENT},
        {"id": "deep_sleep_percentage", "en": "Deep Sleep", "nl": "Diepe Slaap", "u": "%", "i": "mdi:waves", "p": "deep_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "light_sleep_percentage", "en": "Light Sleep", "nl": "Lichte Slaap", "u": "%", "i": "mdi:circle-slice-4", "p": "light_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "rem_sleep_percentage", "en": "REM Sleep", "nl": "REM Slaap", "u": "%", "i": "mdi:eye-check", "p": "rem_sleep", "sc": SensorStateClass.MEASUREMENT},
        {"id": "awake_percentage", "en": "Awake", "nl": "Wakker", "u": "%", "i": "mdi:clock-outline", "p": "awake", "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_snore", "en": "Snoring", "nl": "Snurken", "u": "keer", "i": "mdi:reproduction", "t": True, "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_talk", "en": "Talking", "nl": "Praten", "u": "keer", "i": "mdi:account-voice", "t": True, "sc": SensorStateClass.MEASUREMENT},
        {"id": "sound_event_cough", "en": "Coughing", "nl": "Hoesten", "u": "keer", "i": "mdi:alert-decagram", "t": True, "sc": SensorStateClass.MEASUREMENT},
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
            _LOGGER.error("Fout bij SleepAsAndroid MQTT message: %s", e)

    await async_subscribe(hass, topic, global_msg_recv)

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
        self.counts = {k: 0 for k in ["sound_event_snore", "sound_event_talk", "sound_event_cough", "sound_event_laugh", "sound_event_yawn", "sound_event_sniff"]}
        self.count_times = {k: ("Nog niet" if self.lang == 'nl' else "Not yet") for k in self.counts.keys()}
        self.last_event = "Geen data" if self.lang == 'nl' else "No data"
        self.start_time_str = "Niet gestart" if self.lang == 'nl' else "Not started"
        self.stop_time_str = "Niet gestopt" if self.lang == 'nl' else "Not stopped"
        self.alarm_time_str = "Nog niet afgegaan" if self.lang == 'nl' else "Not triggered"
        self.last_sync_str = "Nooit" if self.lang == 'nl' else "Never"

    def process_event(self, event):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.last_sync_str = timestamp
        
        # Start of Pauze (volgens jouw redenering beide direct starten)
        if event in ["sleep_tracking_started", "sleep_tracking_paused"]:
            if not self.unix_start:
                self.reset()
                self.unix_start = time.time()
                self.start_time_str = timestamp
            
            self.is_tracking = True
            self.last_event_time = time.time()
            self.current_phase_num = 4 # Wakker
            self.current_phase_key = "awake"
            self.current_phase_text = "Wakker" if self.lang == 'nl' else "Awake"
            self.last_event = event
            return

        # Auto-start voor gemiste events
        if event in ["deep_sleep", "light_sleep", "rem_sleep", "awake"] and not self.unix_start:
            self.reset()
            self.unix_start = time.time()
            self.start_time_str = timestamp + " (Auto)"
            self.is_tracking = True
            self.last_event_time = time.time()

        # Tijdregistratie
        if self.is_tracking:
            now = time.time()
            if self.last_event_time:
                duration = now - self.last_event_time
                if self.current_phase_key in self.totals:
                    self.totals[self.current_phase_key] += duration
            self.last_event_time = now

        # Fase afhandeling & "In slaap gevallen" detectie
        if event == "sleep_tracking_stopped":
            self.is_tracking = False
            self.unix_stop = time.time()
            self.stop_time_str = timestamp
            self.current_phase_num = 0
            self.current_phase_text = "Standby"
        elif event in ["deep_sleep", "light_sleep", "rem_sleep"]:
            # Leg tijd vast bij de allereerste echte slaapfase
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
    def __init__(self, tracker, device_name, s, lang, unique_dev_id):
        self._tracker, self._id, self._lang = tracker, s["id"], lang
        self._unique_dev_id = unique_dev_id
        friendly_name = s["nl"] if lang == 'nl' else s["en"]
        self._attr_name = f"{device_name} {friendly_name}"
        self._attr_unit_of_measurement = s.get("u")
        self._attr_icon = s["i"]
        self._attr_unique_id = f"sleep_custom_{unique_dev_id}_{s['id']}"
        self._attr_state_class = s.get("sc")
        self._phase_key = s.get("p")
        self._is_counter = s.get("t", False)
        self._extra_attrs = {}

    @property
    def extra_state_attributes(self): return self._extra_attrs

    @property
    def state(self):
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
            attr_key = "weergave" if self._lang == 'nl' else "display"
            self._extra_attrs = {attr_key: f"{h}u {m}m" if self._lang == 'nl' else f"{h}h {m}m"}
            return round(total_sec / 3600, 2)

        if self._id == "efficiency":
            # Efficiëntie berekend over de hele tijd vanaf start/pauze
            awake_t = self._tracker.totals.get("awake", 0)
            if self._tracker.is_tracking and self._tracker.current_phase_key == "awake":
                awake_t += (time.time() - self._tracker.last_event_time)
            sleep_t = max(0, total_sec - awake_t)
            return round((sleep_t / total_sec) * 100, 1) if total_sec > 0 else 0

        if self._is_counter:
            attr_key = "laatst_gedetecteerd" if self._lang == 'nl' else "last_detected"
            self._extra_attrs = {attr_key: self._tracker.count_times.get(self._id)}
            return self._tracker.counts.get(self._id, 0)
        
        if self._phase_key:
            phase_time = self._tracker.totals.get(self._phase_key, 0)
            if self._tracker.is_tracking and self._tracker.current_phase_key == self._phase_key:
                phase_time += (time.time() - self._tracker.last_event_time)
            
            h, m = int(phase_time // 3600), int((phase_time % 3600) // 60)
            attr_time = "tijd_weergave" if self._lang == 'nl' else "time_display"
            self._extra_attrs = {attr_time: f"{h}u {m}m" if self._lang == 'nl' else f"{h}h {m}m"}
            return round((phase_time / total_sec) * 100, 1) if total_sec > 0 else 0

        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_dev_id)},
            "name": f"SleepAsAndroid MQTT Custom ({self._device_display_name})"
        }
