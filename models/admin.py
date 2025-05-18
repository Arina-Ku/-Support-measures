from sqlalchemy.testing.pickleable import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extenctions import db, login_manager

@login_manager.user_loader
def load_user(idAdmin):
    return Admin.query.get(int(idAdmin))

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    idAdmin = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    login = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False)

    support_measures = db.relationship('SupportMeasure', backref='admin', lazy=True)

    def get_id(self):
        return str(self.idAdmin)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)