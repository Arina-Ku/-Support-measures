from ..extenctions import db

class Region(db.Model):
    __tablename__ = 'region'

    idRegion = db.Column(db.Integer, primary_key=True)
    regionName = db.Column(db.String(80), unique=True, nullable=False)

    measure_links = db.relationship('MeasureRegion', backref='region', lazy=True)