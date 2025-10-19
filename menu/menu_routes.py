from flask import Blueprint, jsonify
from models import Category, Service

menu_bp = Blueprint("menu_bp", __name__, url_prefix="/api/menu")

# Get all categories with their services (customer view)
@menu_bp.route("/", methods=["GET"])
def get_menu():
    categories = Category.query.all()
    result = []
    for c in categories:
        services = Service.query.filter_by(category_id=c.id).all()
        result.append({
            "category_id": c.id,
            "category_name": c.name,
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "full_price": s.full_price,
                    "discount_price": s.discount_price
                }
                for s in services
            ]
        })
    return jsonify(result)
