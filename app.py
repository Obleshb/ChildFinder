import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # ✅ Import Flask-Migrate
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)  # ✅ Define db before using it
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "default-secret")  # Load secret key

# Check if DATABASE_URL is set
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set. Check your .env file.")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload config
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions with app
db.init_app(app)  # ✅ Initialize db AFTER defining it
migrate = Migrate(app, db)  # ✅ Initialize Flask-Migrate
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import and register blueprints
from auth import auth_bp
from routes import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
