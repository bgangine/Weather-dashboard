from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import csv
import datetime

# Database imports
from backend.database.init_db import create_tables, get_db

# Weather API utility
from backend.utils.weather_api import fetch_weather_data

app = Flask(__name__)

from backend.utils.weather_api import fetch_weather_data

print(fetch_weather_data("London"))


# Initialize tables on startup
with app.app_context():
    create_tables()

@app.route('/')
def serve_index():
    """
    Serve the main UI (index.html).
    When you go to http://127.0.0.1:5000/ in the browser,
    this will show your weather dashboard interface.
    """
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """
    Serve any static file (CSS, JS, images, etc.) from the 'frontend' folder.
    Example: /styles.css or /app.js
    """
    return send_from_directory('frontend', filename)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Endpoint to get weather data for a given city and date.
    - Checks the local DB for an entry matching (city, date).
    - If found, returns it.
    - If not found, fetches fresh data from the weather API and stores it.
    """
    city = request.args.get('city')
    date_str = request.args.get('date')  # 'YYYY-MM-DD'

    if not city or not date_str:
        return jsonify({
            "error": "Please provide both city and date. Example: /api/weather?city=London&date=2025-03-20"
        }), 400

    # Validate date format
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Check if we already have data for (city, date)
    cursor.execute("""
        SELECT * FROM weather_records
        WHERE city = ? AND date = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (city, date_str))
    row = cursor.fetchone()

    if row:
        # Found data for this city & date
        conn.close()
        return jsonify({
            "city": row['city'],
            "date": row['date'],
            "temperature": row['temperature'],
            "humidity": row['humidity'],
            "wind_speed": row['wind_speed'],
            "air_quality": row['air_quality'],
            "uv_index": row['uv_index'],
            "latitude": row['latitude'],
            "longitude": row['longitude'],
            "created_at": row['created_at']
        })
    else:
        # 2. Fetch fresh data from the API
        weather_info = fetch_weather_data(city)
        if 'error' in weather_info:
            conn.close()
            return jsonify(weather_info), 500
        
        # 3. Insert new data into DB (store it with the requested date)
        cursor.execute("""
            INSERT INTO weather_records
            (city, date, temperature, humidity, wind_speed, air_quality, uv_index, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            city,
            date_str,
            weather_info.get('temperature'),
            weather_info.get('humidity'),
            weather_info.get('wind_speed'),
            weather_info.get('air_quality'),
            weather_info.get('uv_index'),
            weather_info.get('latitude'),
            weather_info.get('longitude')
        ))
        conn.commit()

        # Retrieve the newly inserted row
        cursor.execute("SELECT * FROM weather_records WHERE id = last_insert_rowid()")
        new_row = cursor.fetchone()
        conn.close()
        
        return jsonify({
            "city": new_row['city'],
            "date": new_row['date'],
            "temperature": new_row['temperature'],
            "humidity": new_row['humidity'],
            "wind_speed": new_row['wind_speed'],
            "air_quality": new_row['air_quality'],
            "uv_index": new_row['uv_index'],
            "latitude": new_row['latitude'],
            "longitude": new_row['longitude'],
            "created_at": new_row['created_at']
        })

@app.route('/api/export', methods=['GET'])
def export_data():
    """
    Endpoint to export weather data from the DB into CSV.
    Accepts optional query params: city, start_date, end_date.
    Writes the file to 'exports/' folder and returns the file for download.
    """
    city = request.args.get('city')
    start_date = request.args.get('start_date')  # format: YYYY-MM-DD
    end_date = request.args.get('end_date')      # format: YYYY-MM-DD
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM weather_records WHERE 1=1"
    params = []
    
    if city:
        query += " AND city = ?"
        params.append(city)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return jsonify({"message": "No data found for the given filters"}), 404
    
    # Build CSV
    filename = f"weather_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path = os.path.join("exports", filename)
    
    with open(export_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["id", "city", "date", "temperature", "humidity", "wind_speed",
                         "air_quality", "uv_index", "latitude", "longitude", "created_at"])
        # Write rows
        for row in rows:
            writer.writerow([
                row['id'], row['city'], row['date'], row['temperature'], row['humidity'],
                row['wind_speed'], row['air_quality'], row['uv_index'],
                row['latitude'], row['longitude'], row['created_at']
            ])
    
    return send_file(export_path, as_attachment=True)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
