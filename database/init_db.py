import sqlite3
import os

# Path to the SQLite database file in the 'db' folder
DB_NAME = "weather.db"
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "db",
    DB_NAME
)

def get_db():
    """
    Establish a connection to the SQLite database.
    Returns a connection object with row_factory set to Row.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """
    Create the required tables if they do not already exist.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        air_quality REAL,
        uv_index REAL,
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
