from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Category, Admin
from admin_auth.admin_auth import session_required

category_bp = Blueprint("category_bp", __name__, url_prefix="/api/categories")

# -------------------- HELPER --------------------
def get_current_admin():
    """Get the currently authenticated admin from JWT."""
    admin_id = get_jwt_identity()
    if not admin_id:
        return None
    return Admin.query.get(admin_id)

# -------------------- CREATE CATEGORY --------------------
@category_bp.route("/", methods=["POST"])
@jwt_required()
@session_required
def create_category():
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    try:
        new_category = Category(
            name=data.get("name"),
            description=data.get("description"),
            icon=data.get("icon"),
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify({
            "id": new_category.id,
            "name": new_category.name,
            "description": new_category.description,
            "icon": new_category.icon,
            "message": "Category created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# -------------------- GET ALL CATEGORIES --------------------
@category_bp.route("/", methods=["GET"])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "icon": c.icon,
            } for c in categories
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- GET SINGLE CATEGORY --------------------
@category_bp.route("/<int:category_id>/", methods=["GET"])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "icon": category.icon,
    })

# -------------------- UPDATE CATEGORY --------------------
@category_bp.route("/<int:category_id>/", methods=["PUT"])
@jwt_required()
@session_required
def update_category(category_id):
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    category = Category.query.get_or_404(category_id)
    try:
        category.name = data.get("name", category.name)
        category.description = data.get("description", category.description)
        category.icon = data.get("icon", category.icon)
        db.session.commit()
        return jsonify({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "icon": category.icon,
            "message": "Category updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# -------------------- DELETE CATEGORY --------------------
@category_bp.route("/<int:category_id>/", methods=["DELETE"])
@jwt_required()
@session_required
def delete_category(category_id):
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    category = Category.query.get_or_404(category_id)
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
