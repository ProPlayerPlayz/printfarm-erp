import unittest
from app import create_app, db
from app.models import User, Order, PrintJob, Printer, OrderStatus, JobStatus, UserRole
from app.services.analytics_service import AnalyticsService
from datetime import datetime, timedelta

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create Dummy Data
        self.user = User(email='admin@test.com', name='Admin', role=UserRole.ADMIN)
        self.user.set_password('password')
        db.session.add(self.user)
        
        self.printer = Printer(name='TestPrinter', status='idle')
        db.session.add(self.printer)
        db.session.commit()
        
        # Order 1: Yesterday
        self.o1 = Order(customer_user_id=self.user.id, created_at=datetime.utcnow() - timedelta(days=1))
        db.session.add(self.o1)
        
        # Order 2: Today
        self.o2 = Order(customer_user_id=self.user.id, created_at=datetime.utcnow())
        db.session.add(self.o2)
        db.session.commit()
        
        # Job for Order 1
        self.j1 = PrintJob(
            order_id=self.o1.id, 
            material_type='PLA', 
            color='Black',
            estimated_material_grams=100, 
            assigned_printer_id=self.printer.id,
            stl_path='dummy.stl',
            original_filename='dummy.stl'
        )
        db.session.add(self.j1)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_orders_per_day(self):
        data = AnalyticsService.get_orders_per_day(days=7)
        # Should have counts for today and yesterday
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        counts = {d['date']: d['count'] for d in data}
        print(f"DEBUG: Data: {data}")
        print(f"DEBUG: Counts Keys: {list(counts.keys())}")
        print(f"DEBUG: Today: {today_str}")
        self.assertEqual(counts.get(today_str), 1)
        self.assertEqual(counts.get(yesterday_str), 1)

    def test_filament_usage(self):
        data = AnalyticsService.get_filament_usage_stats()
        # Should contain PLA: 100
        pla_stat = next((d for d in data if d['material'] == 'PLA'), None)
        self.assertIsNotNone(pla_stat)
        self.assertEqual(pla_stat['grams'], 100)

    def test_analytics_api_access(self):
        # Login
        self.client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'password'})
        
        response = self.client.get('/analytics/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('orders_per_day', data)
        self.assertIn('filament_usage', data)

    def test_analytics_api_forbidden(self):
        # No login
        response = self.client.get('/analytics/api/stats')
        self.assertEqual(response.status_code, 302) # Redirects to login

if __name__ == '__main__':
    unittest.main()
