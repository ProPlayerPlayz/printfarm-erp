import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Order, PrintJob, UserRole, OrderStatus, JobStatus
from app.customer.forms import NewOrderForm
from app.services.storage import save_file
from app.services.pricing import calculate_estimate
from app.services.workflow import transition_order_status
from app.services.audit import log_action
from app.auth.decorators import role_required

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/home')
def home():
    return render_template('customer/home.html')

@customer_bp.route('/order/new', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.CUSTOMER)
def order_new():
    form = NewOrderForm()
    if form.validate_on_submit():
        uploaded_files = request.files.getlist('stl_files')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('No files selected', 'danger')
            return render_template('customer/order_new.html', form=form)

        # Create Order in REVIEW status
        order = Order(
            customer_user_id=current_user.id,
            status=OrderStatus.REVIEW,
            priority=False, 
            shipping_address=current_user.customer_profile.address_line1 if current_user.customer_profile else "No Address",
            created_at=db.func.now()
        )
        db.session.add(order)
        db.session.flush() # get ID
        
        total_estimate = 0
        
        for file in uploaded_files:
            if file and file.filename.endswith('.stl'):
                # Save file
                rel_path = save_file(file, order.id)
                
                # Create Job
                # Estimate placeholder: 50g, 60min default
                est_grams = 50 
                est_mins = 60
                qty = form.quantity.data
                
                job_price = calculate_estimate(est_grams, est_mins, qty)
                total_estimate += job_price
                
                job = PrintJob(
                    order_id=order.id,
                    stl_path=rel_path,
                    original_filename=secure_filename(file.filename),
                    material_type=form.material_type.data,
                    color=form.color.data,
                    quantity=qty,
                    estimated_time_minutes=est_mins,
                    estimated_material_grams=est_grams,
                    status=JobStatus.WAITING,
                )
                db.session.add(job)
        
        order.total_estimated_price = total_estimate
        
        # Don't log create yet? Or log 'draft'?
        db.session.commit()
        
        return redirect(url_for('customer.order_confirm', id=order.id))

    return render_template('customer/order_new.html', form=form)

@customer_bp.route('/order/<int:id>/confirm', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.CUSTOMER)
def order_confirm(id):
    order = Order.query.get_or_404(id)
    if order.customer_user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customer.orders'))
        
    if order.status != OrderStatus.REVIEW:
        # If already confirmed, just go to detail
        return redirect(url_for('customer.order_detail', id=order.id))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'confirm':
            order.status = OrderStatus.NEW
            log_action(current_user.id, "create_order", "Order", order.id)
            db.session.commit()
            flash(f'Order #{order.id} confirmed and placed!', 'success')
            return redirect(url_for('customer.orders'))
        elif action == 'cancel':
            db.session.delete(order) # Cascades jobs hopefully? check models. Yes backref cascade.
            db.session.commit()
            flash('Order cancelled.', 'info')
            return redirect(url_for('customer.home'))
            
    shipping_cost = 15.00
    grand_total = float(order.total_estimated_price) + shipping_cost
    return render_template('customer/order_confirmation.html', order=order, shipping_cost=shipping_cost, grand_total=grand_total)

@customer_bp.route('/orders')
@login_required
@role_required(UserRole.CUSTOMER)
def orders():
    # Exclude REVIEW status from main list?
    user_orders = Order.query.filter(
        Order.customer_user_id == current_user.id,
        Order.status != OrderStatus.REVIEW
    ).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=user_orders)

@customer_bp.route('/orders/<int:id>')
@login_required
@role_required(UserRole.CUSTOMER)
def order_detail(id):
    order = Order.query.get_or_404(id)
    # Ensure ownership
    if order.customer_user_id != current_user.id:
        flash('You do not have access to that order.', 'danger')
        return redirect(url_for('customer.orders'))
        
    return render_template('customer/order_detail.html', order=order)
