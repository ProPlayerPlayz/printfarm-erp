import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def test_login_flow():
    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing to isolate logic
    
    with app.test_client() as client:
        # Check if user exists
        with app.app_context():
            u = User.query.filter_by(email='admin@local.test').first()
            if not u:
                print("FAIL: Admin user not found in DB.")
                return
            else:
                print("DB: Admin user found.")
                
        # Attempt Login
        print("Attempting login POST...")
        response = client.post('/auth/login', data={
            'email': 'admin@local.test',
            'password': 'password'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            # Check if we are at admin dashboard
            if b'Admin Dashboard' in response.data:
                print("SUCCESS: Login successful, redirected to Admin Dashboard.")
            elif b'Invalid email or password' in response.data:
                print("FAIL: Login returned 'Invalid email or password'.")
            else:
                print("FAIL: Login successful but landed on unexpected page.")
                if b'<li><strong>' in response.data:
                    print("FORM ERRORS FOUND:")
                    print(response.data.decode('utf-8')) # Decode to see text
                else:
                    print(response.data[:500])
        else:
            print(f"FAIL: Login POST returned status {response.status_code}")

if __name__ == "__main__":
    test_login_flow()
