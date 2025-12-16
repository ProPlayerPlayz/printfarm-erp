import unittest
import threading
import time
from app import create_app, db
from app.models import User, Printer, PrintJob, Filament, JobStatus, PrinterStatus
from app.services.workflow import assign_job
from app.services.inventory import consume_filament

class TestConcurrency(unittest.TestCase):
    def setUp(self):
        # Use a temporary file-based DB for concurrency testing to share state across threads
        import os
        self.db_path = 'test_concurrency.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.app = create_app('testing')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        self.printer = Printer(name='ConPrinter', status=PrinterStatus.IDLE)
        db.session.add(self.printer)
        
        self.filament = Filament(material_type='PLA', color='Red', stock_grams=100)
        db.session.add(self.filament)
        db.session.commit()
        
        # Create user
        self.user = User(email='tester@test.com', name='Tester')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        import os
        if os.path.exists(self.db_path):
            # os.remove(self.db_path) # Permission error likely on Windows if connection open
            pass

    def test_concurrent_filament_consumption(self):
        """Test multiple threads consuming filament simultaneously."""
        # Total 100g. 10 threads consume 20g each. 
        # Without locking, maybe >5 succeed? Or stock goes negative?
        
        success_count = 0
        lock = threading.Lock()
        
        def consume_task():
            nonlocal success_count
            with self.app.app_context():
                try:
                    # Refreshing logic happens inside service usually
                    consume_filament(self.filament.id, 20.0)
                    with lock:
                        success_count += 1
                except ValueError:
                    pass
                except Exception as e:
                    print(f"Thread error: {e}")

        threads = [threading.Thread(target=consume_task) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        # Reload filament
        db.session.expire_all()
        f = Filament.query.get(self.filament.id)
        
        print(f"DEBUG: Successes: {success_count}, Final Stock: {f.stock_grams}")
        
        # Expect exactly 5 successes (100 / 20 = 5)
        self.assertEqual(success_count, 5, f"Expected 5 successful consumptions, got {success_count}")
        self.assertEqual(f.stock_grams, 0)

    def test_concurrent_job_assignment(self):
        """Test multiple threads assigning different jobs to the SAME printer."""
        # 5 Jobs
        jobs = []
        for i in range(5):
            j = PrintJob(
                order_id=1, stl_path='x', original_filename='x', 
                material_type='PLA', color='Red', status=JobStatus.WAITING
            )
            db.session.add(j)
        # Verify order FK? Mock order needed.
        from app.models import Order
        o = Order(customer_user_id=self.user.id)
        db.session.add(o)
        db.session.commit()
        for j in jobs: j.order_id = o.id
        db.session.commit()
        
        job_ids = [j.id for j in jobs]
        printer_id = self.printer.id
        user_id = self.user.id
        
        success_count = 0
        errors = []
        lock = threading.Lock()

        def assign_task(jid):
            nonlocal success_count
            with self.app.app_context():
                try:
                    # Load job
                    j_thread = PrintJob.query.get(jid)
                    assign_job(j_thread, printer_id, user_id)
                    with lock:
                        success_count += 1
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    with lock:
                        errors.append(str(e))

        threads = [threading.Thread(target=assign_task, args=(jid,)) for jid in job_ids]
        for t in threads: t.start()
        for t in threads: t.join()
        
        # Only 1 succeeds
        print(f"DEBUG: Assignment Successes: {success_count}, Errors: {len(errors)}")
        self.assertEqual(success_count, 1, "Only 1 job should be assigned to the printer")
        
        # Verify Printer Status
        p = Printer.query.get(printer_id)
        self.assertIsNotNone(p.current_job_id)

if __name__ == '__main__':
    unittest.main()
