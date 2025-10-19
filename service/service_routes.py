from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Service, Admin
from admin_auth.admin_auth import session_required

service_bp = Blueprint("service_bp", __name__, url_prefix="/api/services")

# -------------------- HELPER --------------------
def get_current_admin():
    """Get the currently authenticated admin from JWT."""
    admin_id = get_jwt_identity()
    if not admin_id:
        return None
    return Admin.query.get(int(admin_id))  # Convert string back to int for database query

# -------------------- CREATE SERVICE --------------------
@service_bp.route("/", methods=["POST"])
@jwt_required()
@session_required
def create_service():
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    
    # Handle benefits - convert string to list if needed
    benefits_data = data.get("benefits")
    if isinstance(benefits_data, str) and benefits_data:
        benefits_data = benefits_data.split(", ")
    
    # Handle procedure - convert string to list if needed
    procedure_data = data.get("procedure")
    if isinstance(procedure_data, str) and procedure_data:
        procedure_data = procedure_data.split(", ")
    
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
    return jsonify({"message": "Service created", "id": service.id}), 201

# -------------------- GET ALL SERVICES --------------------
@service_bp.route("/", methods=["GET"])
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
    return jsonify(result)

# -------------------- GET SINGLE SERVICE --------------------
@service_bp.route("/<int:id>", methods=["GET"])
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
    })

# -------------------- UPDATE SERVICE --------------------
@service_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@session_required
def update_service(id):
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    s = Service.query.get_or_404(id)
    data = request.get_json()
    
    # Debug logging
    print(f"=== UPDATING SERVICE {id} ===")
    print(f"Admin: {current_admin.username}")
    print(f"Request data: {data}")
    print(f"Service found: {s.name}")
    
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
        print(f"Service updated successfully: {s.name}")
        return jsonify({"message": "Service updated", "id": s.id})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating service: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Error updating service: {str(e)}"}), 500

# -------------------- DELETE SERVICE --------------------
@service_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@session_required
def delete_service(id):
    current_admin = get_current_admin()
    if not current_admin:
        return jsonify({"message": "Unauthorized"}), 401

    s = Service.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "Service deleted"})
