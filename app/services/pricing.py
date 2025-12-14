def calculate_estimate(grams, minutes, quantity=1):
    """
    Simple deterministic pricing estimator.
    """
    RATE_PER_GRAM = 0.50  # cents/money unit per gram
    RATE_PER_MINUTE = 0.10 # cents/money unit per minute
    BASE_FEE = 5.00       # Setup fee per job
    
    material_cost = grams * RATE_PER_GRAM
    time_cost = minutes * RATE_PER_MINUTE
    
    single_unit_price = material_cost + time_cost + BASE_FEE
    total_price = single_unit_price * quantity
    
    return round(total_price, 2)
