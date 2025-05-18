from ..extenctions import db

class MeasureRegion(db.Model):
    __tablename__ = 'measure_region'

    id = db.Column(db.Integer, primary_key=True)
    measureID = db.Column(db.Integer, db.ForeignKey('supportMeasures.idSupportMeasure'), nullable=False)
    regionID = db.Column(db.Integer, db.ForeignKey('region.idRegion'), nullable=False)
