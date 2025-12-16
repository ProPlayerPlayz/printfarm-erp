from app.extensions import db
from app.models import Filament, SparePart

def check_filament_stock(filament_id, grams_needed):
    filament = Filament.query.get(filament_id)
    if not filament:
        return False, "Filament not found"
    
    if filament.stock_grams < grams_needed:
        return False, f"Insufficient stock. Available: {filament.stock_grams}g, Needed: {grams_needed}g"
        
    return True, "Stock available"

def consume_filament(filament_id, grams):
    """
    Deducts stock. Caller handles transaction/commit or adds to session.
    """
    # Use with_for_update to lock the row
    # SQLite note: FOR UPDATE is not supported, so this might be ignored or handled by generic file locking.
    filament = Filament.query.filter_by(id=filament_id).with_for_update().first()
    if filament:
        # Check stock again under lock? 
        # Actually with_for_update works on the initial query.
        # But here we are getting by ID.
        # Ideally: db.session.query(Filament).with_for_update().filter_by(id=filament_id).first()
        
        filament.stock_grams = max(0, filament.stock_grams - grams)
        # Note: Caller commits. If caller (finish_job) doesn't commit immediately, lock is held.
        # This is good.
        return True
    return False

def get_reorder_suggestions():
    """
    Returns lists of filaments and parts that are below reorder level.
    """
    low_filaments = Filament.query.filter(Filament.stock_grams <= Filament.reorder_level_grams).all()
    low_parts = SparePart.query.filter(SparePart.stock_qty <= SparePart.reorder_level_qty).all()
    
    return {
        'filaments': low_filaments,
        'parts': low_parts
    }
