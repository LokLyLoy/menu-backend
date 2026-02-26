from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import create_engine, text
import os

from routes.admin.service import service_bp
from routes.admin.user import user_bp
from routes.admin.category import category_bp
from routes.admin.auth import auth_bp
from extensions import db, jwt
from models import User

app = Flask(__name__)

# Database config (PostgreSQL / Neon)
# Prefer DATABASE_URL env var; fall back to your Neon URL for local/dev.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_O17gXTBMDEch@ep-super-art-a13f862y-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
)

# Normalize to use psycopg (psycopg3) driver with SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Set to True if you want CSRF protection
app.config["JWT_COOKIE_SAMESITE"] = "Lax"

# Init extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)
CORS(app,
     origins=["http://localhost:3000", "http://192.168.1.168:8000/", "http://192.168.1.168:8000", "http://192.168.1.168:3000/", "http://192.168.1.168:3000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Set-Cookie"],
     supports_credentials=True)


#register
app.register_blueprint(service_bp)
app.register_blueprint(user_bp)
app.register_blueprint(category_bp)
app.register_blueprint(auth_bp)

# blocklist
REVOKE_JTIS = set()

# @app.post("/login")
# def login():
#     data = request.get_json()
#
#     username = data.get("username", None)
#     password = data.get("password", None)
#
#     if not username or not password:
#         return jsonify({"msg": "username and password are required"}), 400
#
#     user = User.query.filter_by(username=username).first()
#
#     if not user:
#         return jsonify({"msg": "incorrect username or password"}), 401
#
#     user_id = str(user.id)
#     password_match = check_password_hash(user.password, password)
#
#     if password_match:
#         access_token = create_access_token(identity=user_id)
#         return jsonify({"access_token": access_token}), 200
#     else:
#         return jsonify({"msg": "incorrect username or password"}), 401
#
# @app.get("/me")
# @jwt_required()
# def get_me():
#     user = get_jwt_identity()
#     return jsonify({"user": user}), 200
#
# @app.post("/logout")
# @jwt_required()
# def logout():
#     jti = get_jwt()["jti"]
#     REVOKE_JTIS.add(jti)
#     return jsonify({"msg": "logout successful"}), 200

if __name__ == "__main__":
    app.run(debug=True)
