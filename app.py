from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder=".")
CORS(app)

# In-memory store: { "YYYY-MM-DD": {"name": "X", "date": "YYYY-MM-DD"} }
reservations = {}

# Serve the chalet.html file
@app.route("/")
def index():
    return send_from_directory(".", "chalet.html")

# API: Get all reservations
@app.route("/api/reservations", methods=["GET"])
def get_reservations():
    return jsonify(reservations)

# API: Create reservation
@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.get_json()
    name = data.get("name")
    date = data.get("date")

    if not name or not date:
        return jsonify({"error": "Missing name or date"}), 400
    if date in reservations:
        return jsonify({"error": "Date already reserved"}), 400

    reservations[date] = {"name": name, "date": date}
    return jsonify({"message": "Reservation created", "reservation": reservations[date]}), 201

# API: Search reservations by name
@app.route("/api/reservations/search", methods=["GET"])
def search_reservation():
    query = request.args.get("name", "").lower()
    results = {d: r for d, r in reservations.items() if query in r["name"].lower()}
    return jsonify(results)

# API: Update reservation
@app.route("/api/reservations/<date>", methods=["PUT"])
def update_reservation(date):
    if date not in reservations:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    new_name = data.get("name", reservations[date]["name"])
    new_date = data.get("date", date)

    if new_date != date and new_date in reservations:
        return jsonify({"error": "New date already reserved"}), 400

    # Move reservation if date changed
    reservations.pop(date)
    reservations[new_date] = {"name": new_name, "date": new_date}
    return jsonify({"message": "Reservation updated", "reservation": reservations[new_date]})

# API: Delete reservation
@app.route("/api/reservations/<date>", methods=["DELETE"])
def delete_reservation(date):
    if date not in reservations:
        return jsonify({"error": "Reservation not found"}), 404
    reservations.pop(date)
    return jsonify({"message": "Reservation deleted"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
