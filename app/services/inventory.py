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
    filament = Filament.query.get(filament_id)
    if filament:
        filament.stock_grams = max(0, filament.stock_grams - grams)
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
