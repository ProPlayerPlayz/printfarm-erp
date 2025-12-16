import unittest
from app import create_app, db
from app.models import User, Printer, UserRole, PrinterStatus

class TestAdminPrinters(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create Admin User
        self.admin = User(email='admin@test.com', name='Admin', role=UserRole.ADMIN)
        self.admin.set_password('password')
        db.session.add(self.admin)
        db.session.commit()
        
        self.client = self.app.test_client()
        self.client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'password'}, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_printer(self):
        response = self.client.post('/admin/printers/new', data={
            'name': 'NewPrinter',
            'location': 'Shelf A',
            'notes': 'Test Note'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        p = Printer.query.filter_by(name='NewPrinter').first()
        self.assertIsNotNone(p)
        self.assertEqual(p.location, 'Shelf A')

    def test_edit_printer(self):
        p = Printer(name='OldName', location='OldLoc')
        db.session.add(p)
        db.session.commit()
        
        response = self.client.post(f'/admin/printers/{p.id}/edit', data={
            'name': 'NewName',
            'location': 'NewLoc',
            'notes': 'Updated'
        }, follow_redirects=True)
        
        p_updated = Printer.query.get(p.id)
        self.assertEqual(p_updated.name, 'NewName')

    def test_delete_printer(self):
        p = Printer(name='ToDelete')
        db.session.add(p)
        db.session.commit()
        
        response = self.client.post(f'/admin/printers/{p.id}/delete', follow_redirects=True)
        
        p_deleted = Printer.query.get(p.id)
        self.assertIsNone(p_deleted)

if __name__ == '__main__':
    unittest.main()
