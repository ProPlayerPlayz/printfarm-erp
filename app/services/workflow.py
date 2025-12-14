from datetime import datetime
from app.extensions import db
from app.models import Order, PrintJob, Printer, Shipment, OrderStatus, JobStatus, PrinterStatus, ShipmentStatus
from app.services.audit import log_action
from app.services.inventory import consume_filament

def transition_order_status(order, new_status, user_id, commit=True):
    if order.status == new_status:
        return
        
    old_status = order.status
    order.status = new_status
    
    log_action(
        user_id=user_id,
        action="update_status",
        entity_type="Order",
        entity_id=order.id,
        before={"status": old_status},
        after={"status": new_status}
    )
    
    if commit:
        db.session.commit()

def assign_job(job, printer_id, user_id):
    printer = Printer.query.get(printer_id)
    if not printer:
        raise ValueError("Printer not found")
        
    job.assigned_printer_id = printer_id
    # Log assignment?
    db.session.commit()

def start_job(job, user_id):
    if not job.printer:
        raise ValueError("Job not assigned to printer")
        
    job.status = JobStatus.PRINTING
    job.printer.status = PrinterStatus.PRINTING
    job.printer.current_job_id = job.id
    
    # Also update order status if needed
    if job.order.status in [OrderStatus.NEW, OrderStatus.QUEUED, OrderStatus.REVIEW]:
        transition_order_status(job.order, OrderStatus.PRINTING, user_id, commit=False)
        
    log_action(user_id, "start_job", "PrintJob", job.id)
    db.session.commit()

def finish_job(job, user_id):
    job.status = JobStatus.DONE
    
    if job.printer:
        job.printer.status = PrinterStatus.IDLE
        job.printer.current_job_id = None
        
    # Deduct inventory
    # Assuming 'material_type' and 'color' map to a Filament. 
    # For this simple ERM, we might need a better lookup, but let's assume loose coupling or direct ID wasn't required by prompt.
    # Prompt said: Filament: material_type, color. Job: material_type, color.
    # We find the first matching filament batch.
    
    filament = db.session.query(type(job.printer).query.model).filter_by(
        # Wait, I need Filament model import. Done.
    ).all()
    # Actually, let's fix the logic. We need to query Filament based on job attributes.
    from app.models import Filament
    filament = Filament.query.filter_by(
        material_type=job.material_type, 
        color=job.color
    ).first()
    
    if filament:
        consume_filament(filament.id, job.estimated_material_grams)
    else:
        # Log warning that stock couldn't be deducted?
        pass

    log_action(user_id, "finish_job", "PrintJob", job.id)
    
    # Check if all jobs in order are done
    # db.session.refresh(job.order) 
    # refresh might handle eager loading, but explicit check:
    all_done = all(j.status == JobStatus.DONE for j in job.order.jobs)
    if all_done:
        transition_order_status(job.order, OrderStatus.DONE, user_id, commit=False)
        
    db.session.commit()

def fail_job(job, user_id):
    job.status = JobStatus.FAILED
    if job.printer:
        job.printer.status = PrinterStatus.ERROR
        # Keep assigned but mark error? Or idle?
        # Prompt says: printer -> printing, done -> idle, error -> ?
        # Usually error means intervention needed.
    
    log_action(user_id, "fail_job", "PrintJob", job.id)
    db.session.commit()

def create_shipment(order_id, carrier, tracking, user_id):
    order = Order.query.get(order_id)
    if not order:
        raise ValueError("Order not found")
        
    shipment = Shipment(
        order_id=order_id,
        carrier=carrier,
        tracking_number=tracking,
        status=ShipmentStatus.SHIPPED,
        shipped_at=datetime.utcnow()
    )
    db.session.add(shipment)
    
    transition_order_status(order, OrderStatus.SHIPPED, user_id, commit=False)
    
    log_action(user_id, "create_shipment", "Shipment", order_id, after={"tracking": tracking})
    db.session.commit()
