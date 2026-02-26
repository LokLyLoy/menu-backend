from flask import Blueprint, jsonify, request
from extensions import db
from models import Category

category_bp = Blueprint('category', __name__, url_prefix='/category')

@category_bp.get("/list")
def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        result.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "icon": c.icon,
        })
    return jsonify(result), 200

@category_bp.get("<int:id>")
def get_category(id):
    c = Category.query.get(id)
    return jsonify({
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "icon": c.icon,
    }), 200

@category_bp.post("/create")
def create_category():
    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    icon = data.get("icon")

    if not name:
        return jsonify({"error": "name is required"}), 400

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error": "category already exists"}), 400

    new_category = Category(
        name=name,
        description=description,
        icon=icon,
    )
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "message": "success",
        "category": {
            "id": new_category.id,
            "name": new_category.name,
        }
    }), 200

@category_bp.put("/update/<int:id>")
def update_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({"error": "category not found"}), 404

    data = request.get_json()

    c.name = data.get("name", c.name)
    c.description = data.get("description", c.description)
    c.icon = data.get("icon", c.icon)
    db.session.commit()

    return jsonify({
        "message": "success",
        "category": {
            "id": c.id,
            "name": c.name,
        }
    }), 200

@category_bp.delete("/delete/<int:id>")
def delete_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({"error": "category not found"}), 404

    db.session.delete(c)
    db.session.commit()
    return jsonify({
        "message": "success",
        "category": {
            "id": c.id,
            "name": c.name,
        }
    })