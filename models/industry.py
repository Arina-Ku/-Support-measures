from ..extenctions import db

class Industry(db.Model):
    __tablename__ = 'industry'

    idIndustry = db.Column(db.Integer, primary_key=True)
    industryName = db.Column(db.String(80), unique=True, nullable=False)

    measure_links = db.relationship('MeasureIndustry', backref='industry', lazy=True)

