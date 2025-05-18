from ..extenctions import db

class Category(db.Model):
    __tablename__ = 'category'

    idCategory = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(80), unique=True, nullable=False)

    measure_links = db.relationship('MeasureCategory', backref='category', lazy=True)