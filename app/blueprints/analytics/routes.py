from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.analytics_service import AnalyticsService
from app.models import UserRole, Printer

analytics_bp = Blueprint('analytics', __name__, template_folder='templates')

def check_role():
    if not current_user.is_authenticated:
        return False
    return current_user.role in [UserRole.ADMIN, UserRole.OPS_MANAGER, UserRole.OPERATOR]

@analytics_bp.before_request
@login_required
def require_role():
    if not check_role():
         return "Access Denied", 403

@analytics_bp.route('/')
def dashboard():
    printers = Printer.query.all()
    return render_template('analytics/dashboard.html', printers=printers)

@analytics_bp.route('/api/stats')
def get_stats():
    days = int(request.args.get('days', 30))
    printer_id = request.args.get('printer_id')
    
    if printer_id and printer_id.isdigit():
        printer_id = int(printer_id)
    else:
        printer_id = None

    data = {
        'orders_per_day': AnalyticsService.get_orders_per_day(days, printer_id),
        'order_status': AnalyticsService.get_order_status_distribution(printer_id),
        'filament_usage': AnalyticsService.get_filament_usage_stats(printer_id),
        'printer_utilization': AnalyticsService.get_printer_utilization()
    }
    return jsonify(data)
