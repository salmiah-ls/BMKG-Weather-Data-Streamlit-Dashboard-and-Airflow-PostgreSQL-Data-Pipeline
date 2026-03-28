# Use official slim Airflow image
FROM apache/airflow:slim-2.11.2

USER airflow

# Install extra Python packages
RUN pip install --no-cache-dir requests pandas psycopg2-binary

USER airflow