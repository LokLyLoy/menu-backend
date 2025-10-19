from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from service.service_routes import service_bp
from category.category_routes import category_bp
from menu.menu_routes import menu_bp
from admin_auth.admin_auth import admin_auth, jwt, create_default_admin

app = Flask(__name__)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/menu_api"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change this in production

# Fix trailing slash redirects
app.url_map.strict_slashes = False

# Init extensions
db.init_app(app)
migrate = Migrate(app, db)
CORS(app, 
     origins=["http://localhost:3000", "http://192.168.1.168:8000/", "http://192.168.1.168:8000", "http://192.168.1.168:3000/", "http://192.168.1.168:3000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)
jwt.init_app(app)

# Register blueprints
app.register_blueprint(service_bp)
app.register_blueprint(category_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(admin_auth)

# --- Startup logic for Flask 3.x ---
def setup_admin():
    with app.app_context():
        db.create_all()
        create_default_admin()

# Call setup once at startup
setup_admin()

if __name__ == "__main__":
    app.run(debug=True)
