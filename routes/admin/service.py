from flask import jsonify, request, Blueprint

from extensions import db
from models import Service

service_bp = Blueprint('service', __name__, url_prefix='/service')

@service_bp.get("/list")
def get_services():
    services = Service.query.all()
    result = []
    for s in services:
        result.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "full_price": s.full_price,
            "discount_price": s.discount_price,
            "featured": s.featured,
            "category": {
                "id": s.category.id,
                "name": s.category.name,
                "icon": s.category.icon
            } if s.category else None,
            "benefits": ", ".join(s.benefits) if isinstance(s.benefits, list) and s.benefits else s.benefits,
            "procedure": ", ".join(s.procedure) if isinstance(s.procedure, list) and s.procedure else s.procedure,
            "duration": s.duration,
            "price": s.price
        })
    return jsonify(result), 200

@service_bp.get("/<int:id>")
def get_service(id):
    s = Service.query.get_or_404(id)
    return jsonify({
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "full_price": s.full_price,
        "discount_price": s.discount_price,
        "featured": s.featured,
        "category_id": s.category_id,  # Add this field for frontend
        "category": {
            "id": s.category.id,
            "name": s.category.name,
            "icon": s.category.icon
        } if s.category else None,
        "benefits": ", ".join(s.benefits) if isinstance(s.benefits, list) and s.benefits else s.benefits,
        "procedure": ", ".join(s.procedure) if isinstance(s.procedure, list) and s.procedure else s.procedure,
        "duration": s.duration,
        "price": s.price
    }), 200

@service_bp.post("/create")
def create_service():
    data = request.get_json()

    required_fields = ["name", "full_price", "category_id"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": missing_fields}), 400

    benefits_data = data.get("benefits")
    if isinstance(benefits_data, str) and benefits_data:
        benefits_data = benefits_data.split(", ")

    procedure_data = data.get("procedure")
    if isinstance(procedure_data, str) and procedure_data:
        procedure_data = procedure_data.split(", ")

    existing_service = Service.query.filter_by(name=data["name"]).first()
    if existing_service:
        return jsonify({"error": "service already exists"}), 400

    service = Service(
        name=data["name"],
        description=data.get("description"),
        full_price=data["full_price"],
        discount_price=data.get("discount_price"),
        featured=data.get("featured", False),
        category_id=data["category_id"],
        benefits=benefits_data,
        procedure=procedure_data,
        duration=data.get("duration"),
        price=data.get("price"),
    )

    db.session.add(service)
    db.session.commit()
    return jsonify({
        "message": "service created",
        "service": {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "full_price": service.full_price,
            "discount_price": service.discount_price,
            "featured": service.featured,
            "category_id": service.category_id,
            "benefits": service.benefits,
            "procedure": service.procedure,
            "duration": service.duration,
            "price": service.price
        }
    })

@service_bp.put("/update/<int:id>")
def update_service(id):
    s = Service.query.get_or_404(id)
    if not s:
        return jsonify({"error": "service not found"}), 404

    data = request.get_json()
    required_fields = ["name", "full_price", "category_id"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": missing_fields}), 400

    try:
        s.name = data.get("name", s.name)
        s.description = data.get("description", s.description)
        s.full_price = data.get("full_price", s.full_price)
        s.discount_price = data.get("discount_price", s.discount_price)
        s.featured = data.get("featured", s.featured)
        s.category_id = data.get("category_id", s.category_id)

        # Handle benefits - convert string to list if needed
        benefits_data = data.get("benefits", s.benefits)
        if isinstance(benefits_data, str) and benefits_data:
            s.benefits = benefits_data.split(", ")
        elif isinstance(benefits_data, list):
            s.benefits = benefits_data
        else:
            s.benefits = benefits_data

        # Handle procedure - convert string to list if needed
        procedure_data = data.get("procedure", s.procedure)
        if isinstance(procedure_data, str) and procedure_data:
            s.procedure = procedure_data.split(", ")
        elif isinstance(procedure_data, list):
            s.procedure = procedure_data
        else:
            s.procedure = procedure_data

        s.duration = data.get("duration", s.duration)
        s.price = data.get("price", s.price)

        db.session.commit()

        return jsonify({
            "message": "service updated",
            "service": {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "full_price": s.full_price,
                "discount_price": s.discount_price,
                "featured": s.featured,
                "category_id": s.category_id,
                "benefits": s.benefits,
                "procedure": s.procedure,
                "duration": s.duration,
                "price": s.price
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@service_bp.delete("/delete/<int:id>")
def delete_service(id):
    s = Service.query.get_or_404(id)
    if not s:
        return jsonify({"message": "service not found"}), 404

    db.session.delete(s)
    db.session.commit()

    return jsonify({
        "message": "service deleted",
        "service": {
            "id": s.id,
            "name": s.name,
        }
    }), 200