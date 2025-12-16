from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# --- Enums / Constants ---
class UserRole:
    ADMIN = 'admin'
    OPERATOR = 'operator'
    OPS_MANAGER = 'ops_manager'
    CUSTOMER = 'customer'

class OrderStatus:
    NEW = 'new'
    REVIEW = 'review'
    QUEUED = 'queued'
    PRINTING = 'printing'
    DONE = 'done'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class JobStatus:
    WAITING = 'waiting'
    QUEUED = 'queued'
    PRINTING = 'printing'
    DONE = 'done'
    FAILED = 'failed'

class PrinterStatus:
    IDLE = 'idle'
    PRINTING = 'printing'
    ERROR = 'error'
    MAINTENANCE = 'maintenance'

class ShipmentStatus:
    CREATED = 'created'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

# --- Models ---

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default=UserRole.CUSTOMER, nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)  # Renamed to avoid conflict with UserMixin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer_profile = db.relationship('CustomerProfile', uselist=False, backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return self.is_active_user

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address_line1 = db.Column(db.String(128))
    address_line2 = db.Column(db.String(128))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    pincode = db.Column(db.String(20))
    country = db.Column(db.String(64))

class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    location = db.Column(db.String(64))
    status = db.Column(db.String(20), default=PrinterStatus.IDLE)
    notes = db.Column(db.Text)
    
    current_job_id = db.Column(db.Integer, db.ForeignKey('print_jobs.id'), nullable=True) # Optional back ref helper

class Filament(db.Model):
    __tablename__ = 'filaments'
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(20), nullable=False) # PLA, PETG, ABS
    color = db.Column(db.String(30), nullable=False)
    stock_grams = db.Column(db.Integer, default=0)
    reorder_level_grams = db.Column(db.Integer, default=1000)

class SparePart(db.Model):
    __tablename__ = 'spare_parts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    stock_qty = db.Column(db.Integer, default=0)
    reorder_level_qty = db.Column(db.Integer, default=1)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default=OrderStatus.NEW, index=True)
    priority = db.Column(db.Boolean, default=False)
    shipping_address = db.Column(db.Text) # JSON string snapshot
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Financials
    total_estimated_price = db.Column(db.Numeric(10, 2), default=0.0)
    total_final_price = db.Column(db.Numeric(10, 2), nullable=True)

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_user_id], backref='orders')
    jobs = db.relationship('PrintJob', backref='order', cascade='all, delete-orphan')
    shipment = db.relationship('Shipment', uselist=False, backref='order')

    @property
    def total_weight(self):
        """Calculates total estimated weight of all jobs in the order."""
        return sum(job.estimated_material_grams * job.quantity for job in self.jobs)

class PrintJob(db.Model):
    __tablename__ = 'print_jobs'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    stl_path = db.Column(db.String(256), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    
    material_type = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Estimates per unit
    estimated_time_minutes = db.Column(db.Integer, default=60)
    estimated_material_grams = db.Column(db.Float, default=50.0)
    
    assigned_printer_id = db.Column(db.Integer, db.ForeignKey('printers.id'), nullable=True)
    status = db.Column(db.String(20), default=JobStatus.WAITING, index=True)
    operator_notes = db.Column(db.Text)

    printer = db.relationship('Printer', foreign_keys=[assigned_printer_id], backref='jobs')

class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    carrier = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default=ShipmentStatus.CREATED)
    
    shipped_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50)) # Order, Job, Inventory
    entity_id = db.Column(db.Integer)
    
    before_json = db.Column(db.Text, nullable=True)
    after_json = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    actor = db.relationship('User')
