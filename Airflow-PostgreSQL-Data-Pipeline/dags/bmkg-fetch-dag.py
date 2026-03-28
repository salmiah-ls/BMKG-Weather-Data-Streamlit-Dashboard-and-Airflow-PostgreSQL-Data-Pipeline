from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta, timezone
import requests
import psycopg2

def fetch_bmkg_data():
    url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.71.01.1001"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bmkg_forecast (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP UNIQUE,
            temperature INTEGER,
            weather_desc TEXT,
            fetched_at TIMESTAMP
        );
    """)

    # BMKG API structure can be nested; adding a basic check
    forecast_days = data.get("data", [{}])[0].get("cuaca", [])

    for day in forecast_days:
        for item in day:
            temp = item.get("t")
            raw_time = item.get("datetime")
            weather = item.get("weather_desc")

            if temp is not None and raw_time:
                dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                # dt_wib = dt_utc.astimezone(timezone(timedelta(hours=7)))

                now = datetime.now(timezone.utc)
                
                cur.execute("""
                    INSERT INTO bmkg_forecast (time, temperature, weather_desc, fetched_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (time) 
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        weather_desc = EXCLUDED.weather_desc,
                        fetched_at = EXCLUDED.fetched_at
                """, (dt_utc, temp, weather, now))

    conn.commit()
    cur.close()
    conn.close()
    
# DAG definition
dag = DAG(
    "bmkg_fetch_daily",
    default_args={
        "owner": "you",
        "retries": 1,
        "retry_delay": timedelta(minutes=5)
    },
    start_date=datetime(2026, 3, 27, 0, 0, tzinfo=timezone.utc),  # 7 a.m WIB = 00:00 UTC
    schedule_interval="0 0 * * *",  # daily at 00:00 UTC
    catchup=False
)

task = PythonOperator(
    task_id="fetch_bmkg",
    python_callable=fetch_bmkg_data,
    dag=dag
)
