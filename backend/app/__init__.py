from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from .config import DevelopmentConfig

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=DevelopmentConfig):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    # Set check_same_thread=False for SQLite
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'check_same_thread': False}}

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import all models so SQLAlchemy knows about them before create_all
    with app.app_context():
        from app.models.user import User
        from app.models.student import Student
        from app.models.subject import Subject
        from app.models.attendance import Attendance
        from app.models.assessment import Assessment
        from app.models.topic import Topic
        from app.models.report import Report
        db.create_all()

    # Blueprints
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    from .routes.students import students_bp
    from .routes.subjects import subjects_bp
    from .routes.attendance import attendance_bp
    from .routes.assessments import assessments_bp
    from .routes.topics import topics_bp

    from .routes.reports import reports_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(reports_bp)

    return app
