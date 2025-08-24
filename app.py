from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ✅ Database config (Render/Local)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/chaletdb"
).replace("postgres://", "postgresql://")  # Fix for old-style URLs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ✅ Reservation model
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date.strftime("%Y-%m-%d")
        }

# ✅ Home route (serves chalet.html)
@app.route("/")
def home():
    return render_template("chalet.html")

# ✅ Get all reservations (calendar expects dict)
@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    rows = Reservation.query.all()
    result = {}
    for r in rows:
        result[r.date.strftime("%Y-%m-%d")] = {"name": r.name}
    return jsonify(result)

# ✅ Create a new reservation
@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.get_json()
    name = data.get("name")
    date_str = data.get("date")

    if not name or not date_str:
        return jsonify({"error": "Name and date required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Check if already booked
    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "This date is already reserved"}), 400

    resv = Reservation(name=name, date=date)
    db.session.add(resv)
    db.session.commit()

    return jsonify(resv.to_dict()), 201

# ✅ Delete reservation by date
@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    resv = Reservation.query.filter_by(date=target_date).first()
    if not resv:
        return jsonify({"error": "Reservation not found"}), 404

    db.session.delete(resv)
    db.session.commit()

    return jsonify({"message": "Reservation cancelled"})

# ✅ Search reservations by name
@app.route("/api/reservations/search", methods=["GET"])
def search_reservations():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({})

    rows = Reservation.query.filter(
        Reservation.name.ilike(f"%{name}%")
    ).all()

    result = {}
    for r in rows:
        result[r.date.strftime("%Y-%m-%d")] = {"name": r.name}
    return jsonify(result)


# ✅ Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # make sure tables exist
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
