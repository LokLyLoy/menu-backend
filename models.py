from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Admin Model
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Admin {self.username}>"

# Category Model
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)

    services = db.relationship(
        "Service",
        backref="category",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name}>"

# Service Model
class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    full_price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    # New fields for modal details
    benefits = db.Column(db.JSON, nullable=True)      # list of strings
    procedure = db.Column(db.JSON, nullable=True)     # list of strings
    duration = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Service {self.name} - {self.full_price}>"
