from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ✅ Database config (Render gives DATABASE_URL as env variable)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/chaletdb")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ✅ Reservation model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), unique=True, nullable=False)

# ✅ API routes
@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    reservations = Reservation.query.all()
    return jsonify({r.date: {"name": r.name} for r in reservations})

@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.json
    name = data.get("name")
    date = data.get("date")

    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "This date is already reserved"}), 400

    new_reservation = Reservation(name=name, date=date)
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({"message": "Reservation created", "name": name, "date": date})

@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    reservation = Reservation.query.filter_by(date=date).first()
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"})

@app.route("/api/reservations/search")
def search_reservations():
    name = request.args.get("name")
    results = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    return jsonify({r.date: {"name": r.name} for r in results})

# ✅ Serve frontend (chalet.html)
@app.route("/")
def index():
    return send_from_directory(".", "chalet.html")

# ✅ Run + ensure tables are created
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # 👈 ensures PostgreSQL tables exist
    app.run(host="0.0.0.0", port=5000)
