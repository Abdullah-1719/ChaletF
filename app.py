import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === Database Setup ===
uri = os.getenv("DATABASE_URL")

# Fix prefix if needed
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# === Reservation Model ===
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False, unique=True)  # YYYY-MM-DD format

    def to_dict(self):
        return {"id": self.id, "name": self.name, "date": self.date}


# === Create Tables on Startup ===
@app.before_first_request
def create_tables():
    db.create_all()


# === Routes ===
@app.route("/")
def index():
    return render_template("chalet.html")  # Your frontend file


@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    reservations = Reservation.query.all()
    return jsonify({r.date: r.to_dict() for r in reservations})


@app.route("/api/reservations", methods=["POST"])
def add_reservation():
    data = request.get_json()
    name = data.get("name")
    date = data.get("date")

    if not name or not date:
        return jsonify({"error": "Name and Date are required"}), 400

    # Check if already booked
    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "Date already reserved"}), 400

    new_res = Reservation(name=name, date=date)
    db.session.add(new_res)
    db.session.commit()

    return jsonify(new_res.to_dict()), 201


@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    res = Reservation.query.filter_by(date=date).first()
    if not res:
        return jsonify({"error": "Reservation not found"}), 404

    db.session.delete(res)
    db.session.commit()
    return jsonify({"message": "Reservation cancelled"}), 200


@app.route("/api/reservations/search", methods=["GET"])
def search_reservation():
    name = request.args.get("name")
    results = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    return jsonify({r.date: r.to_dict() for r in results})


# === Run Local ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
