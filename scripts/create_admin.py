import sys
import os

# Add parent dir to path to find 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, UserRole

def create_admin(name, email, password):
    app = create_app('development')
    with app.app_context():
        if User.query.filter_by(email=email).first():
            print(f"Error: User with email {email} already exists.")
            return
            
        admin = User(name=name, email=email, role=UserRole.ADMIN)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {name} ({email}) created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <name> <email> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])
