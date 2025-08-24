from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://chaletdb_user:LsRIQ8uCcwJGjaQ0zchrO3bLWozqQzvU@dpg-d2jhdendiees73c889ug-a/chaletdb"  # adjust for local
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Reservation model
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, unique=True, nullable=False)

# Create tables if not exist
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("chalet.html")

# Get all reservations
@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    reservations = Reservation.query.all()
    result = {r.date.strftime("%Y-%m-%d"): {"name": r.name} for r in reservations}
    return jsonify(result)

# Create a new reservation
@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.get_json()
    name = data.get("name")
    date = data.get("date")

    if not name or not date:
        return jsonify({"error": "Name and Date are required"}), 400

    # Check if date is already reserved
    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "This date is already reserved"}), 400

    new_reservation = Reservation(name=name, date=date)
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({"message": "Reservation created successfully"})

# Delete reservation
@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    reservation = Reservation.query.filter_by(date=date).first()
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"})

# Search reservations by name
@app.route("/api/reservations/search", methods=["GET"])
def search_reservations():
    name = request.args.get("name")
    reservations = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    result = {r.date.strftime("%Y-%m-%d"): {"name": r.name} for r in reservations}
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
