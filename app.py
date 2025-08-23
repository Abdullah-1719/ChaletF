from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("postgresql://chaletdb_user:LsRIQ8uCcwJGjaQ0zchrO3bLWozqQzvU@dpg-d2jhdendiees73c889ug-a/chaletdb")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False, unique=True)

# === Serve the frontend ===
@app.route('/')
def index():
    return send_from_directory('.', 'chalet.html')  # Serve your chalet.html file

# === API Routes ===
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    reservations = Reservation.query.all()
    return jsonify({r.date: {"name": r.name} for r in reservations})

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    name, date = data['name'], data['date']
    if Reservation.query.filter_by(date=date).first():
        return jsonify({"error": "Date already reserved"}), 400
    r = Reservation(name=name, date=date)
    db.session.add(r)
    db.session.commit()
    return jsonify({"message": "Reservation created"})

@app.route('/api/reservations/<date>', methods=['DELETE'])
def delete_reservation(date):
    r = Reservation.query.filter_by(date=date).first()
    if not r:
        return jsonify({"error": "Reservation not found"}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"})

@app.route('/api/reservations/search')
def search_reservation():
    name = request.args.get('name')
    results = Reservation.query.filter(Reservation.name.ilike(f"%{name}%")).all()
    return jsonify({r.date: {"name": r.name} for r in results})

# Run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(host='0.0.0.0', port=5000)
