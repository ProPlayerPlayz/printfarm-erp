from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import Order, PrintJob, Filament, OrderStatus, JobStatus, Printer

class AnalyticsService:
    @staticmethod
    def get_orders_per_day(days=30, printer_id=None):
        """
        Returns a list of dicts: {'date': 'YYYY-MM-DD', 'count': N}
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        query = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        ).filter(Order.created_at >= start_date)

        if printer_id:
            # If printer_id is specified, we filter orders that have at least one job assigned to this printer
            # or strictly we could look at jobs, but "Orders per day" is an Order metric.
            # To make it printer specific, maybe we switch to "Jobs per day" or filter orders containing jobs for this printer.
            # Let's filter orders that have jobs assigned to this printer.
            query = query.join(PrintJob).filter(PrintJob.assigned_printer_id == printer_id)

        stats = query.group_by('date').all()
        
        # Fill in missing days
        results = {}
        for s in stats:
            date_key = s.date
            if not isinstance(date_key, str):
                date_key = date_key.strftime('%Y-%m-%d')
            results[date_key] = s.count
        data = []
        for i in range(days):
            day = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            data.append({'date': day, 'count': results.get(day, 0)})
            
        return data

    @staticmethod
    def get_order_status_distribution(printer_id=None):
        """
        Returns a breakdown of orders by status.
        """
        query = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        )

        if printer_id:
            query = query.join(PrintJob).filter(PrintJob.assigned_printer_id == printer_id)

        stats = query.group_by(Order.status).all()
        return [{'status': s.status, 'count': s.count} for s in stats]

    @staticmethod
    def get_filament_usage_stats(printer_id=None):
        """
        Returns distribution of material types requested in jobs.
        """
        query = db.session.query(
            PrintJob.material_type,
            func.sum(PrintJob.estimated_material_grams).label('total_grams')
        )
        
        if printer_id:
            query = query.filter(PrintJob.assigned_printer_id == printer_id)
            
        stats = query.group_by(PrintJob.material_type).all()
        # Filter out None if any
        return [{'material': s.material_type, 'grams': float(s.total_grams or 0)} for s in stats if s.material_type]

    @staticmethod
    def get_printer_utilization():
        """
        Returns job counts per printer.
        """
        query = db.session.query(
            Printer.name,
            func.count(PrintJob.id).label('job_count')
        ).outerjoin(PrintJob, Printer.id == PrintJob.assigned_printer_id)\
         .group_by(Printer.id)
         
        stats = query.all()
        return [{'printer': s.name, 'jobs': s.job_count} for s in stats]
