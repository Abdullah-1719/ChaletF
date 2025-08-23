from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Use database URL from environment variable (Render provides it)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("postgresql://chaletdb_user:LsRIQ8uCcwJGjaQ0zchrO3bLWozqQzvU@dpg-d2jhdendiees73c889ug-a/chaletdbL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Reservation model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), unique=True, nullable=False)

# Create tables (only first run)
with app.app_context():
    db.create_all()

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
        return jsonify({"error": "Date already reserved"}), 400

    new_reservation = Reservation(name=name, date=date)
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({"success": True, "name": name, "date": date})

@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    reservation = Reservation.query.filter_by(date=date).first()
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/reservations/search")
def search_reservations():
    name = request.args.get("name", "")
    results = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    return jsonify({r.date: {"name": r.name} for r in results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
