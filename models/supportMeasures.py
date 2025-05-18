from ..extenctions import db

class SupportMeasure(db.Model):
    __tablename__ = 'supportMeasures'

    idSupportMeasure = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225), nullable=False)
    description = db.Column(db.String(), nullable=False)
    condition = db.Column(db.String(), nullable=False)
    sourceLink = db.Column(db.String(100), unique=True, nullable=False)
    implementationPeriod = db.Column(db.String(50), nullable=False)

    adminID = db.Column(db.Integer, db.ForeignKey('admin.idAdmin'), nullable=True)

    categories = db.relationship('MeasureCategory', backref='measure', lazy=True)
    industries = db.relationship('MeasureIndustry', backref='measure', lazy=True)
    regions = db.relationship('MeasureRegion', backref='measure', lazy=True)
    brf = db.relationship('MeasureBRF', backref='measure', lazy=True)