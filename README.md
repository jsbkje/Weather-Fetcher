🌤️ K1CTY’s Weather Fetcher v1.0
A real-time desktop dashboard for visualizing NOAA weather forecasts and county-level alerts. Designed with amateur radio operators and weather-conscious users in mind — built for clarity, speed, and zero distraction.

📍 Overview
K1CTY’s Weather Fetcher is a standalone Python GUI application that displays:

Hourly weather forecasts from the U.S. National Weather Service (NOAA)

County-specific active alerts with visual severity cues

An animated 12-hour forecast chart (temperature, wind, precipitation)

Graphical weather icons and alert buttons for rapid interpretation

Audible tone notification when new alerts are detected

Auto-refresh logic for passive monitoring without background daemons or tray icons

The app is self-contained, privacy-conscious, and crafted for operational situational awareness — ideal for ham radio dispatchers, storm spotters, and field operators.

⚙️ Features
Feature	Description
📡 IP-based Geolocation	Automatically detects user’s lat/lon, county, and state via ipinfo.io
🌐 NOAA API Integration	Fetches forecast and alert data from api.weather.gov
🧭 Forecast Display	Shows 5-hour temperature previews with graphical NOAA icons
📊 Animated Chart	Visualizes 12-hour forecast with temperature, wind speed, and precipitation
⚠️ Alert Detection	Filters active alerts by county and severity — with color-coded buttons
🔔 Sound Notification	Plays tone when a new alert ID is detected
🔁 Auto Polling	Refreshes forecast every 1 hour, alerts every 30 minutes
🛡️ Privacy Respectful	No user tracking or data storage — geolocation is used only for NOAA queries
🖼️ GUI Snapshot
(Add screenshots here once the app is running in a production environment.)

🛠️ Installation
Requirements
Install dependencies:

bash
pip install requests pillow matplotlib python-dateutil
Run the App
bash
python Weather_Fetcher.py
The dashboard will launch with auto-detected location and begin fetching your forecast and alerts.

🗃️ Packaging for Windows
To build a standalone .exe:

bash
pyinstaller weather_fetcher.spec
✅ console=False ensures silent GUI startup ✅ upx=False minimizes antivirus false positives ✅ Spec file preconfigured for smooth PyInstaller packaging

🚧 Known Limitations
U.S.-only functionality (NOAA-based)

IP geolocation accuracy may vary — override logic can be added

No tray minimization (removed for simplicity)

🔮 Potential Upgrades
Multi-location support (static callsign, zip code, or coordinates)

Logging or exportable alert history

Radar overlays or severe weather mapping

Icon theming and forecast extensions (multi-day view)

📡 Maintainer
Created by Joshua (K1CTY) 📬 📍 Groton, Connecticut — a dashboard built by an operator for operators.
