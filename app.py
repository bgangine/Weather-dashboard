from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
from scrape_places import get_top_places
from serper_image_search import fetch_images  # NEW

app = Flask(__name__)

# Optional: DB Setup
def init_db():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            unit TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_search():
    data = request.json
    city = data.get('city')
    unit = data.get('unit')

    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("INSERT INTO search_history (city, unit, timestamp) VALUES (?, ?, ?)",
              (city, unit, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/places', methods=['POST'])
def suggest_places():
    data = request.json
    city = data.get("city")
    weather = data.get("weather")

    try:
        places = get_top_places(city, weather)
        return jsonify({"places": places})
    except Exception as e:
        print("Scrape error:", e)
        return jsonify({"places": [city]})

@app.route('/image-search', methods=['POST'])
def image_search():
    data = request.json
    query = data.get("query")

    try:
        images = fetch_images(query)
        return jsonify(images)
    except Exception as e:
        print("Image search error:", e)
        return jsonify([])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
