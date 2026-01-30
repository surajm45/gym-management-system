from app import create_app, db
import traceback

app = create_app()

with app.app_context():
    try:
        print("Dropping all tables (DEVELOPMENT: data will be lost!)")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Tables created successfully.")
    except Exception:
        traceback.print_exc()
