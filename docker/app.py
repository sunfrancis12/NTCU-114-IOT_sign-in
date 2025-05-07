from flask import Flask, request, jsonify, render_template
import qrcode, base64, socket, io, os, time
from datetime import datetime
from extensions import db
from models import Attendance  # OK now
from flask_migrate import Migrate

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

app = Flask(__name__, static_folder="static", template_folder="templates")

# 設定資料庫連線
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.environ.get('DB_USER', 'root')}:"
    f"{os.environ.get('DB_PASSWORD', 'example')}@"
    f"{os.environ.get('DB_HOST', 'localhost')}/"
    f"{os.environ.get('DB_NAME', 'attendance')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

# 匯入模型
from models import Attendance

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_qr", methods=["GET"])
def generate_qr():
    session_id = str(int(datetime.now().timestamp()))
    qr_data = f"http://{local_ip}:5000/scan?session={session_id}"
    qr = qrcode.make(qr_data)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
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
    record = Attendance(name=name, session=session,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        date=today)
    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "簽到成功！"})

@app.route("/attendance", methods=["GET"])
def get_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    records = Attendance.query.filter_by(date=today).all()
    return jsonify([{"name": r.name, "timestamp": r.timestamp} for r in records])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
