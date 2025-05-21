from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from app.routes import identify_bp

load_dotenv()

app = Flask(__name__)
app.register_blueprint(identify_bp)
CORS(app)

# Optional: root route for health check
@app.route('/')
def home():
    return "Backend is running!"

# Load config from config.py or directly from env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run()
