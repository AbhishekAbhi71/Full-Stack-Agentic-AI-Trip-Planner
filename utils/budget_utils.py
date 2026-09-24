from typing import Optional, Literal

def allocate_budget(
    total_budget: Optional[float],
    trip_days: int,
    travelers: int = 1,
    travel_style: str = "balanced",
    trip_type: Literal["oneway", "roundtrip"] = "oneway",
) -> dict:
    """Allocate the group budget and expose group/per-person values."""
    trip_days = max(int(trip_days or 1), 1)
    travelers = max(int(travelers or 1), 1)

    if total_budget is None or float(total_budget) <= 0:
        return {
            "group_total_budget": None,
            "per_person_total_budget": None,
            "travelers": travelers,
            "trip_days": trip_days,
            "per_person_breakdown": {},
            "group_breakdown": {},
        }

    total_budget = float(total_budget)
    per_person_budget = total_budget / travelers

    ratios = {
        "budget": {"flight": 0.30, "hotel": 0.38, "food": 0.14, "local": 0.08, "other": 0.10},
        "balanced": {"flight": 0.35, "hotel": 0.40, "food": 0.12, "local": 0.08, "other": 0.05},
        "comfort": {"flight": 0.40, "hotel": 0.38, "food": 0.10, "local": 0.07, "other": 0.05},
    }
    r = ratios.get(travel_style, ratios["balanced"]).copy()

    if trip_type == "roundtrip":
        r["flight"] += 0.045
        r["hotel"] -= 0.025
        r["food"] -= 0.01
        r["other"] -= 0.01

    if trip_days <= 2:
        r["flight"] += 0.05
        r["hotel"] -= 0.03
        r["food"] -= 0.01
        r["other"] -= 0.01
    elif trip_days >= 5:
        r["flight"] -= 0.05
        r["hotel"] += 0.04
        r["food"] += 0.01

    total_ratio = sum(r.values())
    r = {k: v / total_ratio for k, v in r.items()}

    pp_flight = round(per_person_budget * r["flight"], 2)
    pp_hotel = round(per_person_budget * r["hotel"], 2)
    pp_food = round(per_person_budget * r["food"], 2)
    pp_local = round(per_person_budget * r["local"], 2)
    pp_other = round(per_person_budget - (pp_flight + pp_hotel + pp_food + pp_local), 2)

    nights = max(trip_days - 1, 1)
    pp_hotel_per_night = round(pp_hotel / nights, 2)

    group_flight = round(pp_flight * travelers, 2)
    group_hotel = round(pp_hotel * travelers, 2)
    group_food = round(pp_food * travelers, 2)
    group_local = round(pp_local * travelers, 2)
    group_other = round(pp_other * travelers, 2)
    group_hotel_per_night = round(pp_hotel_per_night * travelers, 2)

    return {
        "group_total_budget": round(total_budget, 2),
        "per_person_total_budget": round(per_person_budget, 2),
        "travelers": travelers,
        "trip_days": trip_days,
        "flight_budget": group_flight,
        "hotel_budget": group_hotel,
        "hotel_budget_per_night": group_hotel_per_night,
        "food_budget": group_food,
        "local_transport_budget": group_local,
        "other_budget": group_other,
        "per_person_breakdown": {
            "flight_budget": pp_flight,
            "hotel_budget": pp_hotel,
            "hotel_budget_per_night": pp_hotel_per_night,
            "food_budget": pp_food,
            "local_transport_budget": pp_local,
            "other_budget": pp_other,
        },
        "group_breakdown": {
            "flight_budget": group_flight,
            "hotel_budget": group_hotel,
            "hotel_budget_per_night": group_hotel_per_night,
            "food_budget": group_food,
            "local_transport_budget": group_local,
            "other_budget": group_other,
        },
    }