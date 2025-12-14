import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, UserRole, Printer, Filament, SparePart, Order, PrintJob, OrderStatus, JobStatus, PrinterStatus
from app.services.inventory import consume_filament

def seed_data():
    app = create_app('development')
    with app.app_context():
        print("Seeding data...")
        
        # 1. Printers
        printer_names = ['Prusa MK3S - 01', 'Prusa MK3S - 02', 'Bambu X1C - 01', 'Ender 3 V2 - 01', 'Voron 2.4 - 01']
        printers = []
        for name in printer_names:
            if not Printer.query.filter_by(name=name).first():
                p = Printer(name=name, location='Rack A', status=PrinterStatus.IDLE)
                db.session.add(p)
                printers.append(p)
        db.session.commit()
        print(f"Created {len(printers)} printers.")

        # 2. Filaments
        filaments_data = [
            ('PLA', 'Black'), ('PLA', 'White'), ('PLA', 'Red'), 
            ('PETG', 'Grey'), ('ABS', 'Black') 
        ]
        for mat, col in filaments_data:
            if not Filament.query.filter_by(material_type=mat, color=col).first():
                f = Filament(material_type=mat, color=col, stock_grams=2000, reorder_level_grams=500)
                db.session.add(f)
        db.session.commit()
        print("Created filaments.")
        
        # 3. Spare Parts
        parts = ['Nozzle 0.4mm', 'Nozzle 0.6mm', 'PEI Sheet', 'Fans', 'Belts']
        for p_name in parts:
            if not SparePart.query.filter_by(name=p_name).first():
                sp = SparePart(name=p_name, stock_qty=5, reorder_level_qty=2)
                db.session.add(sp)
        db.session.commit()
        print("Created spare parts.")

        # 4. Users (Demo)
        if not User.query.filter_by(email="customer@demo.com").first():
            from app.models import CustomerProfile
            cust = User(name="John Doe", email="customer@demo.com", role=UserRole.CUSTOMER)
            cust.set_password("password")
            db.session.add(cust)
            db.session.flush()
            
            profile = CustomerProfile(user_id=cust.id, phone="555-1234", address_line1="123 Main St", city="Demo City", state="DS", pincode="12345", country="DemoLand")
            db.session.add(profile)
            
            # Orders
            o1 = Order(customer_user_id=cust.id, status=OrderStatus.NEW, total_estimated_price=25.50, shipping_address="123 Main St...")
            db.session.add(o1)
            db.session.flush()
            
            j1 = PrintJob(order_id=o1.id, stl_path="demo.stl", original_filename="robot_part.stl", material_type="PLA", color="Black", status=JobStatus.WAITING)
            db.session.add(j1)
            
            o2 = Order(customer_user_id=cust.id, status=OrderStatus.QUEUED, total_estimated_price=40.00, shipping_address="123 Main St...")
            db.session.add(o2)
            db.session.flush()
            
            j2 = PrintJob(order_id=o2.id, stl_path="demo2.stl", original_filename="bracket_pair.stl", material_type="PETG", color="Grey", quantity=2, status=JobStatus.QUEUED)
            # Assign to printer 1
            printer1 = Printer.query.filter_by(name='Prusa MK3S - 01').first()
            if printer1:
                j2.assigned_printer_id = printer1.id
            
            db.session.add(j2)
            
            db.session.commit()
            print("Created demo customer and orders.")

        # 5. User (Operator)
        if not User.query.filter_by(email="operator@demo.com").first():
            op = User(name="Demo Operator", email="operator@demo.com", role=UserRole.OPERATOR)
            op.set_password("password")
            db.session.add(op)
            db.session.commit()
            print("Created demo operator.")

        print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
