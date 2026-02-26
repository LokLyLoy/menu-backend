from flask import request, Blueprint
from werkzeug.security import generate_password_hash
from models.user import User
from flask import jsonify
from extensions import db

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.get("/list")
def user_list():
    users = User.query.all()
    result = [{"id": u.id, "username": u.username, "email": u.email, "password": u.password} for u in users]
    return jsonify(result), 200

@user_bp.get("/<int:user_id>")
def user_get(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404
    return jsonify({"id": user.id, "username": user.username, "email": user.email, "password": user.password}), 200

@user_bp.post("/create")
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "missing required fields"}), 400

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "user already exists"}), 409

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "user created",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    }), 201

@user_bp.put("/update/<int:user_id>")
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    data = request.get_json()
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    new_password = data.get("password")

    if new_password:
        user.password = generate_password_hash(new_password)

    db.session.commit()

    return jsonify({
        "message": "user updated",
        "user": {
            "username": user.username,
            "email": user.email,
        }
    }), 200

@user_bp.delete("/delete/<int:user_id>")
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "user deleted",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }), 200