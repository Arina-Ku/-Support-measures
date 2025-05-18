from ..extenctions import db

class BusinessRegistrationForm(db.Model):
    __tablename__ = 'business_registration_form'

    idBRF = db.Column(db.Integer, primary_key=True)
    BRFName = db.Column(db.String(80), unique=True, nullable=False)

    measure_links = db.relationship('MeasureBRF', backref='brf', lazy=True)
