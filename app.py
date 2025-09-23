# File: app.py (FINAL VERSION with ALL APIs)

import os
import urllib.parse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from ai_model import predict_image

# 1. Initialize the Flask application
app = Flask(__name__)
CORS(app)

# 2. Database Configuration
raw_password = 'Karan@123' # <-- YAHAN APNA PASSWORD DAALO
DB_PASS = urllib.parse.quote_plus(raw_password)
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'sarpamitra_db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 3. Upload Folder Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 4. Database Model Class
class Snake(db.Model):
    __tablename__ = 'snakes'
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(100), unique=True, nullable=False)
    is_venomous = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # --- YEH NAYA FUNCTION ADD HUA HAI ---
    def to_dict(self):
        return {
            'id': self.id,
            'common_name': self.common_name,
            'scientific_name': self.scientific_name,
            'is_venomous': self.is_venomous,
            'description': self.description,
            'image_url': self.image_url
        }
class Rescuer(db.Model):
    __tablename__ = 'rescuers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    is_hospital = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        kind = "Hospital" if self.is_hospital else "Individual"
        return f"<Rescuer {self.id}: {self.name} ({kind})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'phone_number': self.phone_number,
            'is_hospital': self.is_hospital
        }   
# 5. API Endpoints
@app.route('/api/identify', methods=['POST'])
def identify_image_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'}), 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            predictions = predict_image(filepath)
            top_prediction = predictions[0]
            result = {
                'message': 'Identification successful!',
                'snake_name': top_prediction[1].replace('_', ' ').title(),
                'confidence': f"{top_prediction[2]:.2%}"
            }
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': f'AI model prediction failed: {str(e)}'}), 500
    return jsonify({'error': 'An unknown error occurred'}), 500

# --- YEH NAYA ENDPOINT ADD HUA HAI ---
@app.route('/api/snakes', methods=['GET'])
def get_snakes():
    try:
        all_snakes = db.session.execute(db.select(Snake)).scalars().all()
        results = [snake.to_dict() for snake in all_snakes]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- YEH NAYA DYNAMIC ENDPOINT ADD KARNA HAI ---
@app.route('/api/snakes/<int:snake_id>', methods=['GET'])
def get_snake_detail(snake_id):
    try:
        # Naye tareeke se sirf ek saap ko uski ID se dhoondha
        snake = db.session.get(Snake, snake_id)

        if snake:
            # Agar saap mil gaya, toh uska data bheja
            return jsonify(snake.to_dict())
        else:
            # Agar saap nahi mila, toh 404 error bheja
            return jsonify({'error': 'Snake not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        # --- YEH NAYA SEARCH ENDPOINT ADD KARNA HAI ---
@app.route('/api/search', methods=['GET'])
def search_snakes_api():
    try:
        # Start with a base query to get all snakes
        query = db.select(Snake)

        # Get the 'color' parameter from the URL (e.g., /api/search?color=black)
        color_param = request.args.get('color')

        # Agar color parameter URL mein diya gaya hai, toh filter lagao
        if color_param:
            # .ilike() case-insensitive search karta hai
            # Hum description mein color dhoondh rahe hain
            query = query.where(Snake.description.ilike(f'%{color_param}%'))

        # Execute the final query
        matching_snakes = db.session.execute(query).scalars().all()
        
        # Convert results to dictionary format
        results = [snake.to_dict() for snake in matching_snakes]
        
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rescuers', methods=['GET'])
def get_rescuers():
    try:
        all_rescuers = db.session.execute(db.select(Rescuer)).scalars().all()
        results = [rescuer.to_dict() for rescuer in all_rescuers]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
# 6. Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)