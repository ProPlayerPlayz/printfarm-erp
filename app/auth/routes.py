from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit

from app.extensions import db, login_manager
from app.models import User, CustomerProfile, UserRole
from app.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been disabled.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                # Redirect based on role
                if user.role == UserRole.ADMIN:
                    next_page = url_for('admin.dashboard')
                elif user.role == UserRole.OPERATOR:
                    next_page = url_for('operator.dashboard')
                elif user.role == UserRole.OPS_MANAGER:
                    next_page = url_for('ops.dashboard')
                else:
                    next_page = url_for('customer.home')
            
            return redirect(next_page)
        
        flash('Invalid email or password', 'danger')
    
    if form.errors:
        flash('Form validation failed: ' + str(form.errors), 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data, 
            email=form.email.data, 
            role=UserRole.CUSTOMER
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush() # Get ID
        
        profile = CustomerProfile(
            user_id=user.id,
            phone=form.phone.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state=form.state.data,
            pincode=form.pincode.data,
            country=form.country.data
        )
        db.session.add(profile)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register_customer.html', title='Register', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
