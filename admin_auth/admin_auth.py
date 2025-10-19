from flask import Blueprint, request, jsonify, session
from models import Admin, db
from werkzeug.security import check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import json

# Try to import redis, fall back to in-memory storage if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available, using in-memory session storage")

admin_auth = Blueprint("admin_auth", __name__, url_prefix="/api/admin")
jwt = JWTManager()

# Session management with Redis (fallback to in-memory if Redis not available)
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        SESSION_STORE = "redis"
        print("Using Redis for session storage")
    except:
        # Redis is installed but not running
        SESSION_STORE = "memory"
        session_data = {}
        print("Redis not running, using in-memory session storage")
else:
    # Redis not available
    SESSION_STORE = "memory"
    session_data = {}
    print("Using in-memory session storage")

def get_session_data(admin_id):
    """Get session data for admin"""
    if SESSION_STORE == "redis":
        try:
            data = redis_client.get(f"admin_session:{admin_id}")
            return json.loads(data) if data else None
        except:
            return None
    else:
        return session_data.get(admin_id)

def set_session_data(admin_id, data):
    """Set session data for admin"""
    if SESSION_STORE == "redis":
        try:
            redis_client.setex(f"admin_session:{admin_id}", 3600, json.dumps(data))  # 1 hour
        except:
            pass
    else:
        session_data[admin_id] = data

def update_last_activity(admin_id):
    """Update last activity timestamp for admin"""
    current_time = datetime.utcnow().isoformat()
    session_data = get_session_data(admin_id) or {}
    session_data['last_activity'] = current_time
    set_session_data(admin_id, session_data)

def is_session_valid(admin_id):
    """Check if session is still valid (within 1 hour of inactivity)"""
    session_data = get_session_data(admin_id)
    if not session_data or 'last_activity' not in session_data:
        return False
    
    last_activity = datetime.fromisoformat(session_data['last_activity'])
    now = datetime.utcnow()
    return (now - last_activity).total_seconds() < 3600  # 1 hour = 3600 seconds

def session_required(f):
    """Decorator to check session validity and update activity"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = get_jwt_identity()
        
        # Convert admin_id to string for consistency
        admin_id = str(admin_id) if admin_id else None
        
        # Check if session is valid
        if not is_session_valid(admin_id):
            return jsonify({"message": "Session expired. Please login again."}), 401
        
        # Update last activity
        update_last_activity(admin_id)
        
        return f(*args, **kwargs)
    
    return decorated_function

# Auto-create default admin if not exists
def create_default_admin():
    default_username = "admin"
    default_password = "Pnv123123"
    if not Admin.query.filter_by(username=default_username).first():
        admin = Admin(username=default_username, password=default_password)
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin / Pnv123123")

# Login route
@admin_auth.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Create 1-hour session
    access_token = create_access_token(identity=str(admin.id), expires_delta=timedelta(hours=1))
    
    # Initialize session data
    session_data = {
        'last_activity': datetime.utcnow().isoformat(),
        'login_time': datetime.utcnow().isoformat()
    }
    set_session_data(str(admin.id), session_data)
    
    return jsonify({
        "access_token": access_token,
        "expires_in": 3600,  # 1 hour in seconds
        "message": "Login successful"
    }), 200

# Example protected route
@admin_auth.route("/me", methods=["GET"])
@jwt_required()
@session_required
def get_me():
    admin_id = get_jwt_identity()
    admin = Admin.query.get(int(admin_id))  # Convert back to int for database query
    return jsonify({"username": admin.username})

# Refresh session endpoint
@admin_auth.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_session():
    admin_id = get_jwt_identity()
    
    # Convert admin_id to string for consistency
    admin_id = str(admin_id) if admin_id else None
    
    # Check if session is valid
    if not is_session_valid(admin_id):
        return jsonify({"message": "Session expired. Please login again."}), 401
    
    # Update activity and create new token
    update_last_activity(admin_id)
    new_token = create_access_token(identity=str(admin_id), expires_delta=timedelta(hours=1))
    
    return jsonify({
        "access_token": new_token,
        "expires_in": 3600,
        "message": "Session refreshed successfully"
    }), 200

# Logout endpoint
@admin_auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    admin_id = get_jwt_identity()
    
    # Convert admin_id to string for consistency
    admin_id = str(admin_id) if admin_id else None
    
    # Clear session data
    if SESSION_STORE == "redis":
        try:
            redis_client.delete(f"admin_session:{admin_id}")
        except:
            pass
    else:
        session_data.pop(admin_id, None)
    
    return jsonify({"message": "Logged out successfully"}), 200

# Check session status
@admin_auth.route("/session-status", methods=["GET"])
@jwt_required()
def session_status():
    admin_id = get_jwt_identity()
    
    # Convert admin_id to string for consistency
    admin_id = str(admin_id) if admin_id else None
    
    session_data = get_session_data(admin_id)
    
    if not session_data or not is_session_valid(admin_id):
        return jsonify({
            "valid": False,
            "message": "Session expired"
        }), 401
    
    # Calculate remaining time
    last_activity = datetime.fromisoformat(session_data['last_activity'])
    now = datetime.utcnow()
    remaining_seconds = 3600 - (now - last_activity).total_seconds()
    
    return jsonify({
        "valid": True,
        "remaining_seconds": max(0, int(remaining_seconds)),
        "last_activity": session_data['last_activity']
    }), 200
