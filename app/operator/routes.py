from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Order, PrintJob, Printer, UserRole, JobStatus, PrinterStatus
from app.auth.decorators import role_required
from app.services.workflow import start_job, finish_job, fail_job, assign_job

operator_bp = Blueprint('operator', __name__)

@operator_bp.route('/dashboard')
@login_required
@role_required(UserRole.OPERATOR, UserRole.ADMIN)
def dashboard():
    # KPIs
    active_jobs_count = PrintJob.query.filter_by(status=JobStatus.PRINTING).count()
    queued_jobs_count = PrintJob.query.filter_by(status=JobStatus.QUEUED).count()
    printers_count = Printer.query.count()
    printers_error_count = Printer.query.filter_by(status=PrinterStatus.ERROR).count()
    
    # Active Printers
    active_printers = Printer.query.filter_by(status=PrinterStatus.PRINTING).all()
    
    return render_template('operator/dashboard.html', 
                           active_jobs=active_jobs_count,
                           queued_jobs=queued_jobs_count,
                           total_printers=printers_count,
                           error_printers=printers_error_count,
                           active_printers=active_printers)

@operator_bp.route('/jobs')
@login_required
@role_required(UserRole.OPERATOR, UserRole.ADMIN)
def jobs():
    # Filter options could be added here
    waiting_jobs = PrintJob.query.filter_by(status=JobStatus.WAITING).order_by(PrintJob.order_id.asc()).all()
    queued_jobs = PrintJob.query.filter_by(status=JobStatus.QUEUED).all()
    printing_jobs = PrintJob.query.filter_by(status=JobStatus.PRINTING).all()
    
    printers = Printer.query.all()
    
    return render_template('operator/jobs.html', 
                           waiting_jobs=waiting_jobs, 
                           queued_jobs=queued_jobs,
                           printing_jobs=printing_jobs,
                           printers=printers)

@operator_bp.route('/jobs/<int:job_id>/action', methods=['POST'])
@login_required
@role_required(UserRole.OPERATOR, UserRole.ADMIN)
def job_action(job_id):
    job = PrintJob.query.get_or_404(job_id)
    action = request.form.get('action')
    
    try:
        if action == 'assign':
            printer_id = request.form.get('printer_id')
            assign_job(job, printer_id, current_user.id)
            job.status = JobStatus.QUEUED # Explicitly move to queued after assignment? Workflow says so.
            db.session.commit()
            flash(f'Job #{job_id} assigned to printer.', 'success')
            
        elif action == 'start':
            start_job(job, current_user.id)
            flash(f'Job #{job_id} started.', 'success')
            
        elif action == 'finish':
            finish_job(job, current_user.id)
            flash(f'Job #{job_id} marked as completed.', 'success')
            
        elif action == 'fail':
            fail_job(job, current_user.id)
            flash(f'Job #{job_id} marked as failed.', 'warning')
            
        elif action == 'queue':
             # Manual move to queue without printer? Or reset?
             job.status = JobStatus.QUEUED
             db.session.commit()
    except Exception as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('operator.jobs'))

@operator_bp.route('/printers')
@login_required
@role_required(UserRole.OPERATOR, UserRole.ADMIN)
def printers():
    printers = Printer.query.all()
    return render_template('operator/printers.html', printers=printers)

@operator_bp.route('/printers/<int:id>')
@login_required
@role_required(UserRole.OPERATOR, UserRole.ADMIN)
def printer_detail(id):
    printer = Printer.query.get_or_404(id)
    history = PrintJob.query.filter_by(assigned_printer_id=id).order_by(PrintJob.id.desc()).limit(10).all()
    return render_template('operator/printer_detail.html', printer=printer, history=history)
