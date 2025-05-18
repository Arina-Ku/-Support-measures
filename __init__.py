from flask import Flask

from App.ai.recommender_service import recommender_service
from .extenctions import login_manager
from .routes.admin import admin
from .routes.supportMeasure import supportMeasure
from .extenctions import db, migrate
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(admin)
    app.register_blueprint(supportMeasure)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    #recommender_service.init_app(app)

    with app.app_context():
        db.create_all()

    return app