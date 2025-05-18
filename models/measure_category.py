from ..extenctions import db

class MeasureCategory(db.Model):
    __tablename__ = 'measureCategory'

    id = db.Column(db.Integer, primary_key=True)
    measureID = db.Column(db.Integer, db.ForeignKey('supportMeasures.idSupportMeasure'), nullable=False)
    categoryID = db.Column(db.Integer, db.ForeignKey('category.idCategory'), nullable=False)