from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/devices')
def get_devices():
    conn = sqlite3.connect('devices.db')
    c = conn.cursor()
    c.execute("SELECT * FROM devices ORDER BY last_seen DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"mac": r[0], "ip": r[1], "vendor": r[2], "first_seen": r[3], "last_seen": r[4], "is_new": bool(r[5])} for r in rows])

@app.route('/alerts')
def get_alerts():
    # Stub: Pull recent new devices
    conn = sqlite3.connect('devices.db')
    c = conn.cursor()
    c.execute("SELECT * FROM devices WHERE is_new=1 ORDER BY first_seen DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"ip": r[1], "vendor": r[2], "first_seen": r[3]} for r in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)