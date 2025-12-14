import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def check_users():
    app = create_app('development')
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users.")
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Name: {u.name} | Role: {u.role} | Active: {u.is_active_user}")
            # Verify password
            check_pw = "password"
            if u.check_password(check_pw):
                print(f"  -> Password 'password' matches.")
            else:
                print(f"  -> Password 'password' DOES NOT match.")
            
if __name__ == "__main__":
    check_users()
