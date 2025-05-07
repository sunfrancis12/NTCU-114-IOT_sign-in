from extensions import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    session = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))
    date = db.Column(db.String(100))
