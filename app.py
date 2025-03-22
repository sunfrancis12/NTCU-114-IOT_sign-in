from flask import Flask, request, jsonify, render_template
import qrcode
import os
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")

# 確保資料庫存在
def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/generate_qr", methods=["GET"])
def generate_qr():
    session_id = str(int(datetime.now().timestamp()))
    qr_data = f"http://localhost:5000/scan?session={session_id}"
    qr = qrcode.make(qr_data)
    qr.save("qrcode.png")
    return jsonify({"qr_url": qr_data})

@app.route("/scan")
def scan_page():
    session = request.args.get("session")
    return render_template("scan.html", session=session)

@app.route("/scan", methods=["POST"])
def scan_qr():
    data = request.json
    name = data.get("name")
    session = data.get("session")
    
    if not name:
        return jsonify({"error": "Missing name"}), 400
    
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("INSERT INTO attendance (name, session, timestamp) VALUES (?, ?, ?)",
              (name, session, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "簽到成功！"})

@app.route("/attendance", methods=["GET"])
def get_attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT name, timestamp FROM attendance")
    records = c.fetchall()
    conn.close()
    return jsonify([{"name": r[0], "timestamp": r[1]} for r in records])

if __name__ == "__main__":
    app.run(debug=True)
