# backend/app/__init__.py
import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    # ------------------- compute absolute frontend path -------------------
    current_dir = os.path.dirname(os.path.abspath(__file__))   # .../backend/app
    backend_dir = os.path.dirname(current_dir)                 # .../backend
    project_dir = os.path.dirname(backend_dir)                 # .../gym-project
    frontend_dir = os.path.join(project_dir, "frontend")       # .../gym-project/frontend

    # create flask app with absolute static folder
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")

    # ---------------- DATABASE CONFIG ----------------
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Suraj%4045@localhost/gymdb"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "SUPERSECRET123"

    # ---------------- EMAIL CONFIG ----------------
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = "moolyas794@gmail.com"
    app.config['MAIL_PASSWORD'] = "ibcm rtjy lhhb cjvd"  # consider using env vars instead

    # ---------------- INITIALIZE EXTENSIONS ----------------
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    from .routes import members_bp
    from .plan_routes import plan_bp
    from .payment_routes import payment_bp
    from .equipment_routes import equipment_bp
    from .trainer_routes import trainer_bp
    from .attendance_routes import attendance_bp
    from .auth_routes import auth_bp

    app.register_blueprint(members_bp, url_prefix="/api")
    app.register_blueprint(plan_bp, url_prefix="/api")
    app.register_blueprint(payment_bp, url_prefix="/api")
    app.register_blueprint(equipment_bp, url_prefix="/api")
    app.register_blueprint(trainer_bp, url_prefix="/api")
    app.register_blueprint(attendance_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")

    # ---------------- HEALTH CHECK ----------------
    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    # ---------------- SERVE FRONTEND ----------------
    @app.route("/")
    def root():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def serve_page(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        # fallback to index (SPA behaviour)
        return send_from_directory(app.static_folder, "index.html")

    # ---------------- DEBUG helper ----------------
    @app.route("/debug_static")
    def debug_static():
        exists = os.path.exists(app.static_folder)
        sample = []
        try:
            if exists:
                sample = os.listdir(app.static_folder)[:20]
        except Exception:
            sample = ["(cannot list files)"]
        return {"static_folder": app.static_folder, "exists": exists, "sample_files": sample}

    return app
