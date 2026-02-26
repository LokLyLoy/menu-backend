from extensions import db
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