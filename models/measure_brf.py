from ..extenctions import db

class MeasureBRF(db.Model):
    __tablename__ = 'measure_brf'

    id = db.Column(db.Integer, primary_key=True)
    measureID = db.Column(db.Integer, db.ForeignKey('supportMeasures.idSupportMeasure'), nullable=False)
    brfID = db.Column(db.Integer, db.ForeignKey('business_registration_form.idBRF'), nullable=False)
