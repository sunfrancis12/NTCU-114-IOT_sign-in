from flask import Flask, request, jsonify, render_template
import qrcode
import base64
import socket
import io
import os
import sqlite3
from datetime import datetime

# 本地ip
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
    


app = Flask(__name__, static_folder="static", template_folder="templates")

# 確保資料庫存在
def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    session TEXT,
                    timestamp TEXT,
                    date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_qr", methods=["GET"])
def generate_qr():
    session_id = str(int(datetime.now().timestamp()))
    qr_data = f"http://{local_ip}:5000/scan?session={session_id}"
    qr = qrcode.make(qr_data)
    #qr.save("qrcode.png")

    # 轉換為 Base64
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 回傳 Base64 編碼的 QR Code
    return jsonify({"qr_base64": f"data:image/png;base64,{qr_base64}"})

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

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("INSERT INTO attendance (name, session, timestamp, date) VALUES (?, ?, ?, ?)",
              (name, session, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), today))
    conn.commit()
    conn.close()

    return jsonify({"message": "簽到成功！"})

@app.route("/attendance", methods=["GET"])
def get_attendance():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT name, timestamp FROM attendance WHERE date = ?", (today,))
    records = c.fetchall()
    conn.close()
    return jsonify([{"name": r[0], "timestamp": r[1]} for r in records])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
