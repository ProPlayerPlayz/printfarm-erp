import unittest
from app import create_app, db
from app.models import User, PrintJob, Printer, Filament, JobStatus, PrinterStatus
from app.services.workflow import finish_job, start_job
from datetime import datetime

class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        self.user = User(email='op@test.com', name='Operator')
        db.session.add(self.user)
        
        self.printer = Printer(name='P1', status=PrinterStatus.PRINTING)
        db.session.add(self.printer)
        
        # Filament for consumption
        self.filament = Filament(material_type='PLA', color='Black', stock_grams=1000)
        db.session.add(self.filament)
        db.session.commit()
        
        self.job = PrintJob(
            order_id=1, # Mock ID, we might need an order if not testing FK strictness or if order is accessed
            material_type='PLA',
            color='Black',
            estimated_material_grams=50,
            assigned_printer_id=self.printer.id,
            status=JobStatus.PRINTING,
            stl_path='dummy.stl',
            original_filename='dummy.stl'
        )
        # We need an order because finish_job checks job.order.jobs
        from app.models import Order
        self.order = Order(customer_user_id=self.user.id)
        db.session.add(self.order)
        db.session.commit()
        
        self.job.order_id = self.order.id
        db.session.add(self.job)
        
        self.printer.current_job_id = self.job.id
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_finish_job(self):
        """Test that finish_job completes successfully without error."""
        finish_job(self.job, self.user.id)
        
        self.assertEqual(self.job.status, JobStatus.DONE)
        self.assertEqual(self.printer.status, PrinterStatus.IDLE)
        self.assertIsNone(self.printer.current_job_id)
        
        # Verify inventory deduction
        # Refetch filament
        f = Filament.query.get(self.filament.id)
        self.assertEqual(f.stock_grams, 950) # 1000 - 50

    def test_fail_and_retry_job(self):
        """Test failing a job sets printer to maintenance, and retry resets job."""
        from app.services.workflow import fail_job, retry_job
        
        # Fail
        fail_job(self.job, self.user.id)
        self.assertEqual(self.job.status, JobStatus.FAILED)
        self.assertEqual(self.printer.status, PrinterStatus.MAINTENANCE)
        self.assertIsNone(self.printer.current_job_id) # Should be detached
        
        # Retry
        retry_job(self.job, self.user.id)
        self.assertEqual(self.job.status, JobStatus.WAITING)
        self.assertIsNone(self.job.assigned_printer_id) # Should be unassigned


if __name__ == '__main__':
    unittest.main()
