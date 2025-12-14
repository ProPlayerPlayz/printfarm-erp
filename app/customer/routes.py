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

        # Create Order
        order = Order(
            customer_user_id=current_user.id,
            status=OrderStatus.NEW,
            priority=False, # Could add to form
            shipping_address=current_user.customer_profile.address_line1 if current_user.customer_profile else "No Address", # Simplify
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
                # Real implementation would parse STL here
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
        
        log_action(current_user.id, "create_order", "Order", order.id)
        db.session.commit()
        
        flash(f'Order #{order.id} placed successfully!', 'success')
        return redirect(url_for('customer.order_detail', id=order.id))

    return render_template('customer/order_new.html', form=form)

@customer_bp.route('/orders')
@login_required
@role_required(UserRole.CUSTOMER)
def orders():
    user_orders = Order.query.filter_by(customer_user_id=current_user.id).order_by(Order.created_at.desc()).all()
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
