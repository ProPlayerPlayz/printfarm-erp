import unittest
from io import BytesIO
from app import create_app, db
from app.models import User, Order, UserRole, OrderStatus

class TestCustomerOrder(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create Customer
        self.customer = User(email='cust@test.com', name='Customer', role=UserRole.CUSTOMER)
        self.customer.set_password('password')
        db.session.add(self.customer)
        db.session.commit()
        
        self.client = self.app.test_client()
        self.client.post('/auth/login', data={'email': 'cust@test.com', 'password': 'password'}, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_order_flow(self):
        # 1. Submit New Order Form (File Upload)
        data = {
            'stl_files': (BytesIO(b"fake stl content"), 'test.stl'),
            'material_type': 'PLA',
            'color': 'Black',
            'quantity': 1
        }
        response = self.client.post('/customer/order/new', data=data, follow_redirects=False)
        self.assertEqual(response.status_code, 302) # Redirect to confirm
        
        # Get order ID from location or DB
        order = Order.query.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.REVIEW)
        self.assertIn(f'/customer/order/{order.id}/confirm', response.location)
        
        # 2. Access Confirmation Page
        response = self.client.get(f'/customer/order/{order.id}/confirm')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Confirm Your Order', response.data)
        
        # 3. Confirm Order
        response = self.client.post(f'/customer/order/{order.id}/confirm', data={'action': 'confirm'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify status update
        db.session.refresh(order)
        self.assertEqual(order.status, OrderStatus.NEW)

    def test_cancel_order(self):
        # Create Draft Order directly
        order = Order(customer_user_id=self.customer.id, status=OrderStatus.REVIEW)
        db.session.add(order)
        db.session.commit()
        
        # Cancel
        response = self.client.post(f'/customer/order/{order.id}/confirm', data={'action': 'cancel'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        o = Order.query.get(order.id)
        self.assertIsNone(o)

if __name__ == '__main__':
    unittest.main()
