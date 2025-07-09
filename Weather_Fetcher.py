import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from dateutil import parser
import time
import winsound

# ---------------------------------------------
# 🔧 Configuration and Caching
# ---------------------------------------------
USER_AGENT = "K1CTY Weather-Fetcher v1.0 (https://github.com/jsbkje/Weather-Fetcher)"
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
SEVERITY_COLORS = {
    "Extreme": "red", "Severe": "orange", "Moderate": "gold",
    "Minor": "lightyellow", "Unknown": "gray"
}

cached_forecast = None
forecast_timestamp = 0
forecast_refresh_secs = 3600

cached_alerts = None
alerts_timestamp = 0
alerts_refresh_secs = 1800

previous_alert_ids = set()
next_update_label = None

# ---------------------------------------------
# ⏰ Time Formatting
# ---------------------------------------------
def format_time_ampm(timestamp):
    dt = parser.parse(timestamp)
    return dt.strftime("%I%p").lstrip("0")

# ---------------------------------------------
# 📍 Location Retrieval
# ---------------------------------------------
def get_location():
    try:
        data = requests.get("https://ipinfo.io/json").json()
        loc = data["loc"].split(",")
        return loc, data.get("county", ""), data.get("region", "")
    except:
        return None, "", ""

# ---------------------------------------------
# 🌐 NOAA API Access
# ---------------------------------------------
def get_point_metadata(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    return requests.get(url, headers=HEADERS).json()["properties"]

def get_hourly_forecast(metadata):
    url = metadata["forecastHourly"]
    return requests.get(url, headers=HEADERS).json()["properties"]["periods"]

def get_alerts(lat, lon):
    url = f"https://api.weather.gov/alerts?point={lat},{lon}"
    return requests.get(url, headers=HEADERS).json().get("features", [])

# ---------------------------------------------
# 📊 Forecast Plot Animation
# ---------------------------------------------
def animate_forecast_plot(frame, ax, times, temps, winds, pops):
    ax.clear()
    ax.plot(times[:frame], temps[:frame], label="Temp (°F)", color="orangered", marker="o")
    ax.plot(times[:frame], winds[:frame], label="Wind (mph)", color="blue", linestyle="--")
    ax.plot(times[:frame], pops[:frame], label="Precip (%)", color="purple", linestyle=":")
    ax.set_title("12-Hour Forecast")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

# ---------------------------------------------
# ⚠️ Alert Viewer
# ---------------------------------------------
def show_alert_details(alert):
    props = alert["properties"]
    win = tk.Toplevel(root)
    win.title(f"{props['event']} Details")
    win.geometry("500x400")
    tk.Label(win, text=props["headline"], font=("Arial", 12, "bold"), wraplength=480, justify="left").pack(pady=(10,5), anchor="w")
    tk.Label(win, text=f"Severity: {props['severity']}", font=("Arial", 10), fg="red").pack(anchor="w", padx=10)
    tk.Label(win, text="Description:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(15,0))
    desc_text = tk.Text(win, wrap="word", width=60, height=15)
    desc_text.insert("1.0", props["description"])
    desc_text.config(state="disabled")
    desc_text.pack(padx=10, pady=(0,10))

# ---------------------------------------------
# ⚠️ Alert Panel Display
# ---------------------------------------------
def display_alerts(alerts, county):
    for widget in alert_frame.winfo_children():
        widget.destroy()
    tk.Label(alert_frame, text="⚠️ Active Alerts:", font=("Arial", 10, "bold")).pack()

    filtered = []
    for alert in alerts:
        props = alert["properties"]
        try:
            expires = parser.parse(props["expires"])
            if expires < datetime.now(timezone.utc):
                continue
        except:
            continue
        if county and county.lower() not in props["areaDesc"].lower():
            continue
        filtered.append(alert)

    global previous_alert_ids
    current_ids = set(alert["id"] for alert in filtered)
    if current_ids - previous_alert_ids:
        winsound.Beep(750, 300)
    previous_alert_ids = current_ids

    if not filtered:
        tk.Label(alert_frame, text="✅ No alerts for your county", fg="blue").pack()
        return

    for alert in filtered:
        props = alert["properties"]
        color = SEVERITY_COLORS.get(props["severity"], "gray")
        tk.Button(alert_frame, text=f"{props['event']} – {county}",
                  command=lambda a=alert: show_alert_details(a),
                  relief="raised", bg=color, padx=5,
                  wraplength=250, anchor="w", justify="left"
        ).pack(pady=1, fill="x", expand=True)

# ---------------------------------------------
# 🌦️ Weather Display
# ---------------------------------------------
def display_weather():
    loc_data, county, _ = get_location()
    if not loc_data:
        messagebox.showerror("Error", "Could not determine location.")
        return

    lat, lon = loc_data
    now = time.time()

    global cached_forecast, forecast_timestamp, cached_alerts, alerts_timestamp
    if now - forecast_timestamp > forecast_refresh_secs or cached_forecast is None:
        metadata = get_point_metadata(lat, lon)
        cached_forecast = get_hourly_forecast(metadata)
        forecast_timestamp = now
    if now - alerts_timestamp > alerts_refresh_secs or cached_alerts is None:
        cached_alerts = get_alerts(lat, lon)
        alerts_timestamp = now

    forecast = cached_forecast
    alerts = cached_alerts

    for widget in frame_icons.winfo_children():
        widget.destroy()
    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    for i, period in enumerate(forecast[:5]):
        time_txt = format_time_ampm(period["startTime"])
        temp_txt = f"{period['temperature']}°{period['temperatureUnit']}"
        tk.Label(frame_icons, text=time_txt, font=("Arial", 11, "bold")).grid(row=0, column=i, padx=10)
        tk.Label(frame_icons, text=temp_txt, font=("Arial", 11)).grid(row=1, column=i, padx=10)
        icon_img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(period["icon"]).content)).resize((70, 70)))
        lbl = tk.Label(frame_icons, image=icon_img)
        lbl.image = icon_img
        lbl.grid(row=2, column=i, padx=10)

    display_alerts(alerts, county)

    times = [format_time_ampm(p["startTime"]) for p in forecast[:12]]
    temps = [p["temperature"] for p in forecast[:12]]
    winds = [int(p["windSpeed"].split()[0]) if p["windSpeed"] else 0 for p in forecast[:12]]
    pops = [p.get("probabilityOfPrecipitation", {}).get("value", 0) or 0 for p in forecast[:12]]

    fig, ax = plt.subplots(figsize=(5.5, 2.5), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    global weather_animation
    weather_animation = animation.FuncAnimation(fig, animate_forecast_plot, frames=len(times)+1,
                                                fargs=(ax, times, temps, winds, pops),
                                                interval=50, repeat=False)

    # ⏱️ Next update time display
    next_time = datetime.now() + timedelta(seconds=3600)
    next_update_label.config(text=next_time.strftime("Next check: %I:%M:%S %p").lstrip("0"))

# ---------------------------------------------
# 🔁 Auto Poll Scheduler
# ---------------------------------------------
def schedule_poll():
    root.after(3600000, update_weather_if_expired)

def update_weather_if_expired():
    display_weather()
    schedule_poll()

# ---------------------------------------------
# 🖥️ GUI Initialization
# ---------------------------------------------
def initialize_dashboard():
    global left_frame, frame_icons, dashboard_frame, alert_frame, next_update_label

    left_frame = tk.Frame(root)
    left_frame.grid(row=0, column=0, sticky="n", padx=10)

    frame_icons = tk.Frame(left_frame)
    frame_icons.pack()
    dashboard_frame = tk.Frame(left_frame)
    dashboard_frame.pack(pady=10)

    alert_frame = tk.Frame(root, bd=2, relief="groove")
    alert_frame.grid(row=0, column=1, sticky="n", padx=(0,10), pady=10)

    next_update_label = tk.Label(root, font=("Arial", 9), anchor="e", justify="right")
    next_update_label.place(relx=1.0, rely=1.0, x=-10, y=-5, anchor="se")

    display_weather()
    schedule_poll()

    root.update_idletasks()
    
    w = left_frame.winfo_reqwidth() + alert_frame.winfo_reqwidth() + 40
    h = max(left_frame.winfo_reqheight(), alert_frame.winfo_reqheight()) + 30
    root.geometry(f"{w}x{h}")
root = tk.Tk()
root.title("K1CTY's Weather Fetcher v1.0")
initialize_dashboard()
root.mainloop()
