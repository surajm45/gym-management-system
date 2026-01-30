# debug_commit.py
from app import create_app, db
from app.models import Plan, Member
import traceback

app = create_app()

with app.app_context():
    try:
        # quick test: create a plan and a member, then commit
        p = Plan(name="DEBUG PLAN", price=0.0, duration_days=30)
        db.session.add(p)
        db.session.flush()  # push to DB so p.id exists (but not committed yet)

        m = Member(name="Debug User", email="debug@example.com", phone="000", plan_id=p.id)
        db.session.add(m)

        db.session.commit()
        print("DEBUG: Commit succeeded.")
    except Exception as e:
        # print full traceback and the underlying DB error (if present)
        traceback.print_exc()
        # If SQLAlchemy DBAPI error is present, show it:
        try:
            orig = e.__cause__   # SQLAlchemy often chains the DB-API error here
            print("\n== ORIGINAL DB-API ERROR ==")
            print(type(orig), orig)
            # If PyMySQL OperationalError/InternalError appears:
            try:
                print("orig.args:", orig.args)
            except Exception:
                pass
        except Exception:
            pass
        finally:
            # rollback to return session to clean state
            try:
                db.session.rollback()
            except:
                pass
