from extensions import db
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    full_price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    benefits = db.Column(db.JSON, nullable=True)
    procedure = db.Column(db.JSON, nullable=True)
    duration = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)