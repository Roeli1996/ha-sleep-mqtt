# 🌙 Custom SleepAsAndroid MQTT Sensors for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/MAINTAINER-Roeli1996-blue.svg?style=for-the-badge)](https://github.com/Roeli1996)
[![Version](https://img.shields.io/badge/VERSION-1.2.0-green.svg?style=for-the-badge)](https://github.com/Roeli1996/ha-sleep-mqtt/releases)
[![License](https://img.shields.io/badge/LICENSE-MIT-yellow.svg?style=for-the-badge)](LICENSE)

This custom integration brings advanced sleep tracking analytics from the **SleepAsAndroid** app directly into Home Assistant via MQTT. Unlike standard implementations, this version calculates live statistics and features a dedicated **Real-time Hypnogram** sensor for tracking sleep stages as they happen.

---

## ✨ Features

* **📊 Live Hypnogram (Numerical):** Dedicated `Sleep Phase` sensor using numerical values (1-4) for instant compatibility with **ApexCharts** and History Graphs.
* **💤 Fell Asleep Tracking:** New sensor that records the exact timestamp when you actually transition from "Awake" to a sleep stage.
* **🔄 Real-time Calculations:** Live calculation of sleep duration and phase distribution percentages using decimal values for precise graphing.
* **📈 Long-term Statistics:** Full support for Home Assistant Long-Term Statistics (LTS) with `measurement` state classes.
* **🔊 Sound Event Counters:** Specifically tracks occurrences of snoring, talking, coughing, laughing, or yawning.
* **⏰ Smart Start & Pause Support:** Correctly handles "Delayed Start" and "Paused" states in SleepAsAndroid to ensure your sleep graph starts the moment you get into bed.
* **🌍 Multi-language:** Supports English and Dutch natively via official Home Assistant translation files.

---

## 🚀 Installation

### Step 1: Via HACS (Recommended)
1.  Open **HACS** in your Home Assistant instance.
2.  Click the three dots in the top right corner and select **Custom repositories**.
3.  Paste your GitHub repository URL: `https://github.com/Roeli1996/ha-sleep-mqtt`
4.  Select **Integration** as the category and click **Add**.
5.  Search for **SleepAsAndroid MQTT Custom** and click **Download**.
6.  **Restart** Home Assistant.

### Step 2: Configure SleepAsAndroid App
Configure the app on your Android device to broadcast data:
1.  Go to **Settings > Services > MQTT**.
2.  **Enable MQTT.**
3.  **Host:** Your MQTT broker IP (e.g., your Home Assistant / Mosquitto IP).
4.  **Topic prefix:** Use a unique path, e.g., `SleepAsAndroid/Arne`.
5.  **Important:** Ensure **Events** is checked in the MQTT settings to enable the Hypnogram feature.

---

## 📈 Available Sensors (v1.2.0)

| Sensor | State Type | Description | Attributes |
| :--- | :--- | :--- | :--- |
| **Status** | String | Current app activity/event | Last event string |
| **Sleep Phase** | Number (1-4) | Current stage (1:Deep, 2:Light, 3:REM, 4:Awake) | `fase_tekst` (String) |
| **Fell Asleep** | Time | Exact time you transitioned into sleep | - |
| **Sleep Duration** | Float | Total decimal hours (e.g. 7.75) | `weergave` (e.g. 7u 45m) |
| **Efficiency** | Percentage | Percentage of time spent actually sleeping | - |
| **Phase Breakdown** | Percentage | Distribution of Deep, Light, REM, and Awake | `tijd_weergave` |
| **Sound Events** | Counter | Counts of snoring, talking, coughing, etc. | `laatst_gedetecteerd` |

---

## 📝 Changelog

### [1.2.0] - 2026-02-14
#### Added
- **Official Translation Framework:** Refactored code to use `translation_key` and official `strings.json` / `translations` folder.
- **Fell Asleep Sensor:** New dedicated sensor to record the exact moment sleep began.
- **Long-Term Statistics:** Added `state_class: measurement` to enable native HA history analysis.

#### Changed
- **Numerical-First Architecture:** (Breaking Change) Sensors now return numerical values (integers/floats) instead of formatted strings to support native graphing.
- **Smart Session Logic:** Improved handling of `sleep_tracking_paused` events. The integration now initializes the session and sets the phase to "Awake" (4) immediately.
- **Auto-Recovery:** The tracker now auto-starts if a phase event is received but a start event was missed.

---

## 💡 Dashboard Tip
To create a donut chart using **ApexCharts**, use this configuration:

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Slaapverdeling
  show_states: true
  colorize_states: true
chart_type: donut
series:
  - entity: sensor.arne_slaap_diepe_slaap
    name: Diep
    color: "#1A237E"
  - entity: sensor.arne_slaap_rem_slaap
    name: REM
    color: "#4FC3F7"
  - entity: sensor.arne_slaap_lichte_slaap
    name: Licht
    color: "#90CAF9"
  - entity: sensor.arne_slaap_wakker
    name: Wakker
    color: "#FFAB91"
