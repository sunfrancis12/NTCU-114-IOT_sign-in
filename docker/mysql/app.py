from flask import Flask, request, jsonify, render_template
import qrcode
import base64
import socket
import io
from datetime import datetime
import mysql.connector
import os
import time

# 本地ip
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

def wait_for_db():
    time.sleep(10)  # 先等10秒，粗略處理慢啟動
    while True:
        try:
            connection = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", "example"),
                database=os.environ.get("DB_NAME", "attendance")
            )
            print("MySQL is ready!")
            return connection  # ⚠️ 回傳 connection
        except mysql.connector.Error as err:
            print("MySQL not ready, retrying...")
            time.sleep(5)

# 使用回傳的 connection
connection = wait_for_db()


#資料庫
connection = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),     # 這裡會是 'db'
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "example"),
    database=os.environ.get("DB_NAME", "attendance")
)

app = Flask(__name__, static_folder="static", template_folder="templates")

#MySQL資料庫初始化
def init_db():
    # 建立游標物件
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY 
                    name TEXT,
                    session TEXT,
                    timestamp TEXT,
                    date TEXT
                )''')
    cursor.close()
    connection.close()

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

    # 建立游標物件
    cursor = connection.cursor()
    cursor.execute("INSERT INTO attendance (name, session, timestamp, date) VALUES (%s, %s, %s, %s)",
                (name, session, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), today))
    connection.commit()
    cursor.close()

    return jsonify({"message": "簽到成功！"})

@app.route("/attendance", methods=["GET"])
def get_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor = connection.cursor()
    cursor.execute("SELECT name, timestamp FROM attendance WHERE date = ?", (today,))
    records = cursor.fetchall()
    cursor.close()
    
    return jsonify([{"name": r[0], "timestamp": r[1]} for r in records])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
