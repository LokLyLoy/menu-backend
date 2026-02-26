from werkzeug.security import generate_password_hash

from app import app, db
from models import User

with app.app_context():
    db.drop_all()
    db.create_all()

    users = [
        User(username="admin", email="admin@gmail.com", password=generate_password_hash("admin123"))
    ]
    db.session.add_all(users)
    db.session.commit()
    print("Seed data created successfully!")