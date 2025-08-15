# utils.py
def calculate_risk_score(vehicle_use, vehicle_age, sum_insured, driver_age):
    """
    Estimate risk score based on normalized factors instead of a fixed point system.
    Returns (risk_percent, risk_label).
    """

    # Normalize values to a 0-1 scale
    age_factor = min(vehicle_age / 20, 1)        # Older vehicles more risky
    sum_factor = min(sum_insured / 10_000_000, 1) # Higher sum insured more risky
    driver_factor = 1 if driver_age < 25 or driver_age > 70 else 0.5
    use_factor = 1 if vehicle_use == "commercial" else (0.7 if vehicle_use == "other" else 0.4)

    # Weighted risk calculation
    risk_percent = (
        (age_factor * 0.25) +
        (sum_factor * 0.25) +
        (driver_factor * 0.25) +
        (use_factor * 0.25)
    ) * 100

    # Risk label
    if risk_percent >= 70:
        risk_label = "High Risk"
    elif risk_percent >= 40:
        risk_label = "Medium Risk"
    else:
        risk_label = "Low Risk"

    return risk_percent, risk_label
