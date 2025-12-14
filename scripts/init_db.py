import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def init_db():
    app = create_app('development')
    with app.app_context():
        # In a real deployed app with migrations, we use 'flask db upgrade'
        # But for new setup 'create_all' is convenient
        print("Creating all tables...")
        db.create_all()
        print("Database initialized.")

if __name__ == "__main__":
    init_db()
