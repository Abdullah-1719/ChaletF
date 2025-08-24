from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ==============================
# Database Configuration
# ==============================
# Use the DATABASE_URL from Render environment if available
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://chaletdb_user:LsRIQ8uCcwJGjaQ0zchrO3bLWozqQzvU@dpg-d2jhdendiees73c889ug-a.oregon-postgres.render.com/chaletdb"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==============================
# Database Model
# ==============================
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "date": self.date}


# ==============================
# Routes
# ==============================

@app.route("/", methods=["GET"])
def home():
    """Serve the frontend page"""
    return render_template("chalet.html")


@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    """Get all reservations"""
    reservations = Reservation.query.all()
    return jsonify({r.date: r.to_dict() for r in reservations})


@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    """Create a new reservation"""
    data = request.json
    name = data.get("name")
    date = data.get("date")

    if not name or not date:
        return jsonify({"error": "Missing name or date"}), 400

    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "This date is already reserved"}), 400

    new_reservation = Reservation(name=name, date=date)
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify(new_reservation.to_dict()), 201


@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    """Cancel a reservation by date"""
    reservation = Reservation.query.filter_by(date=date).first()
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"}), 200


@app.route("/api/reservations/search", methods=["GET"])
def search_reservation():
    """Search reservations by name"""
    name = request.args.get("name")
    if not name:
        return jsonify({})

    reservations = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    return jsonify({r.date: r.to_dict() for r in reservations})


# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
