import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt

now_wib = datetime.now(timezone(timedelta(hours=7)))
current_date = now_wib.strftime("%A, %d %B %Y %H:%M WIB")
st.markdown(
    f"<div style='text-align: right;'>📅 {current_date}</div>", unsafe_allow_html=True
)

# ===== Title =====
st.title("🌦️ BMKG Weather Dashboard")

# ===== Fetch Data =====
url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.71.01.1001"
data = requests.get(url).json()

# ===== Header Info =====
location = data["data"][0]["lokasi"]

st.metric("📍 Location", f"{location.get('kecamatan')}, {location.get('kotkab')}")


# ===== Process Data =====
rows = []

for item in data["data"][0]["cuaca"][0]:
    temp = item.get("t")
    raw_time = item.get("datetime")
    weather = item.get("weather_desc")

    if temp and raw_time:
        dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        dt_wib = dt_utc.astimezone(timezone(timedelta(hours=7)))

        rows.append({
            "time": dt_wib,
            "temperature": temp,
            "weather_desc": weather
        })

df = pd.DataFrame(rows)

# Format time for display
df["time_str"] = df["time"].dt.strftime("%H:%M")

# ===== Show Table =====
df = df.rename(columns={"time_str": "Time (WIB)", "temperature": "Temperature (°C)", "weather_desc": "Cuaca"})
st.dataframe(df[["Time (WIB)", "Temperature (°C)", "Cuaca"]], hide_index=True)

# ===== Plot Chart =====
st.markdown(
    "<h3 style='text-align: center;'>📋 Temperature Forecast</h3>",
    unsafe_allow_html=True
)
fig, ax = plt.subplots()
ax.plot(df["Time (WIB)"], df["Temperature (°C)"])
#ax.set_title("Temperature Forecast (WIB)")
ax.set_xlabel("Time (WIB)")
ax.set_ylabel("Temperature (°C)")

st.pyplot(fig)
