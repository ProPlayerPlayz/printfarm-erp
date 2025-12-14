from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models import Order, PrintJob, Filament, SparePart, Shipment, UserRole, OrderStatus, ShipmentStatus
from app.auth.decorators import role_required
from app.services.inventory import check_filament_stock, get_reorder_suggestions
from app.services.workflow import create_shipment
from app.services.audit import log_action

ops_bp = Blueprint('ops', __name__)

@ops_bp.route('/dashboard')
@login_required
@role_required(UserRole.OPS_MANAGER, UserRole.ADMIN)
def dashboard():
    # KPIs
    low_stock = get_reorder_suggestions()
    low_stock_count = len(low_stock['filaments']) + len(low_stock['parts'])
    
    orders_to_ship_count = Order.query.filter_by(status=OrderStatus.DONE).count()
    todays_shipments_count = Shipment.query.filter(db.func.date(Shipment.shipped_at) == datetime.utcnow().date()).count()
    
    return render_template('ops/dashboard.html', 
                           low_stock_count=low_stock_count,
                           orders_to_ship=orders_to_ship_count,
                           todays_shipments=todays_shipments_count)

@ops_bp.route('/inventory/filament', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.OPS_MANAGER, UserRole.ADMIN)
def inventory_filament():
    if request.method == 'POST':
        # Simple update logic
        id = request.form.get('id')
        new_stock = request.form.get('stock_grams')
        
        filament = Filament.query.get(id)
        if filament:
            old_stock = filament.stock_grams
            filament.stock_grams = int(new_stock)
            log_action(current_user.id, "update_stock", "Filament", id, 
                       before={'stock': old_stock}, after={'stock': filament.stock_grams})
            db.session.commit()
            flash('Stock updated', 'success')
            return redirect(url_for('ops.inventory_filament'))
            
    filaments = Filament.query.all()
    return render_template('ops/filament.html', filaments=filaments)

@ops_bp.route('/shipments', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.OPS_MANAGER, UserRole.ADMIN)
def shipments():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        carrier = request.form.get('carrier')
        tracking = request.form.get('tracking')
        
        try:
            create_shipment(order_id, carrier, tracking, current_user.id)
            flash(f'Shipment created for Order #{order_id}', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('ops.shipments'))
        
    ready_orders = Order.query.filter_by(status=OrderStatus.DONE).all()
    recent_shipments = Shipment.query.order_by(Shipment.shipped_at.desc()).limit(20).all()
    
    return render_template('ops/shipments.html', ready_orders=ready_orders, shipments=recent_shipments)

@ops_bp.route('/reorder')
@login_required
@role_required(UserRole.OPS_MANAGER, UserRole.ADMIN)
def reorder():
    suggestions = get_reorder_suggestions()
    return render_template('ops/reorder.html', suggestions=suggestions)
