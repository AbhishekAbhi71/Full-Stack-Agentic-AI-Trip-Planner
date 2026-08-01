from typing import Optional


def allocate_budget(total_budget: Optional[float], trip_days: int, travel_style: str = "balanced") -> dict:
    if not total_budget or total_budget <= 0:
        return {
            "flight_budget": None,
            "hotel_budget": None,
            "hotel_budget_per_night": None,
            "food_budget": None,
            "local_transport_budget": None,
            "other_budget": None,
        }

    ratios = {
        "budget": {"flight": 0.30, "hotel": 0.38, "food": 0.14, "local": 0.08, "other": 0.10},
        "balanced": {"flight": 0.35, "hotel": 0.40, "food": 0.12, "local": 0.08, "other": 0.05},
        "comfort": {"flight": 0.40, "hotel": 0.38, "food": 0.10, "local": 0.07, "other": 0.05},
    }

    r = ratios.get(travel_style, ratios["balanced"]).copy()

    if trip_days <= 2:
        r["flight"] += 0.05
        r["hotel"] -= 0.03
        r["food"] -= 0.01
        r["other"] -= 0.01
    elif trip_days >= 5:
        r["flight"] -= 0.05
        r["hotel"] += 0.04
        r["food"] += 0.01

    hotel_budget_total = round(total_budget * r["hotel"], 2)
    hotel_budget_per_night = round(hotel_budget_total / trip_days, 2) if trip_days > 0 else 0

    return {
        "flight_budget": round(total_budget * r["flight"], 2),
        "hotel_budget": hotel_budget_total,
        "hotel_budget_per_night": hotel_budget_per_night,
        "food_budget": round(total_budget * r["food"], 2),
        "local_transport_budget": round(total_budget * r["local"], 2),
        "other_budget": round(total_budget * r["other"], 2),
        "trip_days": trip_days,
    }