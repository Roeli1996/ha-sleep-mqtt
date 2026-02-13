SleepAsAndroid MQTT Custom for Home Assistant

This custom integration brings advanced sleep tracking analytics from the SleepAsAndroid app directly into Home Assistant via MQTT. Unlike the standard integration, this version calculates live statistics such as sleep phases, efficiency, and specific sound events (snoring, talking, etc.) in real-time as you sleep.

✨ Features

🔄 Live Updates: Real-time calculation of sleep duration and phases (Deep, Light, REM).

📊 Sleep Efficiency: Automatic calculation of your sleep quality percentage.

🔊 Event Counters: Specifically tracks how many times you snore, talk, cough, laugh, or yawn.

⏰ Alarm Tracking: Records the exact time your alarm started ringing.

👥 Multi-Device Support: Easily add multiple people/phones as separate devices without data conflicts.

🌍 Multi-language: Automatically detects your Home Assistant language (supports English and Dutch).

🚀 Installation

Step 1: Via HACS (Recommended)
Open HACS in your Home Assistant instance.

Click the three dots in the top right corner and select Custom repositories.

Paste the URL of your GitHub repository and select Integration as the category.

Click Install.

Restart Home Assistant.

Step 2: Configure SleepAsAndroid App
To send data to Home Assistant, configure the app on your Android device:

Go to Settings > Services > MQTT.

Enable MQTT.

Host: Your MQTT broker IP (e.g., your Mosquitto add-on address).

Topic prefix: Use a unique path for each person, e.g., SleepAsAndroid/Arne.

Client ID: Choose a unique name for the device.

Step 3: Add the Integration
Go to Settings > Devices & Services.

Click Add Integration and search for SleepAsAndroid MQTT Custom.

Fill in the requested details:

Device Name: The name you want to see in HA (e.g., Arne).

Topic Prefix: The exact same path used in the app (e.g., SleepAsAndroid/Arne).

📈 Available Sensors
The following sensors are created for each device:

Status: Current activity of the app (tracking, paused, etc.).

Sleep Duration: Total time spent in bed (Formatted as 7h 15m, with a decimal attribute).

Sleep Efficiency: Percentage of time spent actually sleeping.

Sleep Phases: Deep, Light, REM, and Awake (shown in % with duration attributes).

Sound Events: Counters for snoring, coughing, talking, etc. (includes last_detected attribute).

Alarm Time: The time the last alarm was triggered.

Last Sync: Timestamp of the last received MQTT message.

🛠 Support & Development
This is a custom integration. If you find a bug or have a suggestion, please open an Issue on the GitHub repository.
