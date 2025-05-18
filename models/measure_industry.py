from ..extenctions import db

class MeasureIndustry(db.Model):
    __tablename__ = 'measure_industry'

    id = db.Column(db.Integer, primary_key=True)
    measureID = db.Column(db.Integer, db.ForeignKey('supportMeasures.idSupportMeasure'), nullable=False)
    industryID = db.Column(db.Integer, db.ForeignKey('industry.idIndustry'), nullable=False)
