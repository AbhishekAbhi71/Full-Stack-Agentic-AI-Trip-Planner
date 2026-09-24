from datetime import datetime
from langchain_core.messages import AIMessage,SystemMessage
import json
from graph.state import MessagesState
from utils.budget_utils import allocate_budget

def validate_trip_request(trip: dict) -> dict:
    """Validate the canonical travel request after deterministic overrides."""
    errors = []
    origin = str(trip.get("origin") or "").strip()
    destination = str(trip.get("destination") or "").strip()
    travelers = trip.get("travelers")
    trip_days = trip.get("trip_days")
    budget = trip.get("total_budget")
    trip_type = trip.get("trip_type")
    departure_date = trip.get("departure_date")
    return_date = trip.get("return_date")

    if not origin:
        errors.append("origin city is missing")
    if not destination:
        errors.append("destination city is missing")

    try:
        travelers = int(travelers)
        if travelers < 1:
            errors.append("travelers must be at least 1")
    except (TypeError, ValueError):
        errors.append("travelers must be a valid positive integer")

    try:
        trip_days = int(trip_days)
        if trip_days < 1:
            errors.append("trip_days must be at least 1")
    except (TypeError, ValueError):
        errors.append("trip_days must be a valid positive integer")

    if budget is not None:
        try:
            budget = float(budget)
            if budget <= 0:
                errors.append("total_budget must be greater than 0")
        except (TypeError, ValueError):
            errors.append("total_budget must be a valid number")

    if trip_type not in {"oneway", "roundtrip"}:
        errors.append("trip_type must be oneway or roundtrip")

    if departure_date:
        try:
            datetime.strptime(departure_date, "%Y-%m-%d")
        except ValueError:
            errors.append("departure_date must be YYYY-MM-DD")

    if return_date:
        try:
            datetime.strptime(return_date, "%Y-%m-%d")
        except ValueError:
            errors.append("return_date must be YYYY-MM-DD")

    if departure_date and return_date:
        try:
            dep = datetime.strptime(departure_date, "%Y-%m-%d").date()
            ret = datetime.strptime(return_date, "%Y-%m-%d").date()
            if ret <= dep:
                errors.append("return_date must be after departure_date")
        except ValueError:
            pass

    if errors:
        raise ValueError("Invalid travel request: " + "; ".join(errors))

    trip["origin"] = origin
    trip["destination"] = destination
    trip["travelers"] = travelers
    trip["trip_days"] = trip_days
    trip["total_budget"] = budget

    if return_date:
        trip["trip_type"] = "roundtrip"

    if departure_date and return_date:
        dep = datetime.strptime(departure_date, "%Y-%m-%d").date()
        ret = datetime.strptime(return_date, "%Y-%m-%d").date()
        trip["trip_days"] = (ret - dep).days + 1

    return trip

def validator(state: MessagesState):
    """Canonical validation layer between planner and search assistant."""
    trip_request = dict(state.get("trip_request", {}))

    try:
        trip_request = validate_trip_request(trip_request)
    except ValueError as exc:
        return {
            "messages": [AIMessage(content=str(exc))]
        }

    budget_plan = allocate_budget(
        total_budget=trip_request.get("total_budget"),
        trip_days=trip_request.get("trip_days", 1),
        travelers=trip_request.get("travelers", 1),
        travel_style=trip_request.get("travel_style", "balanced"),
        trip_type=trip_request.get("trip_type", "oneway"),
    )

    return {
        "trip_request": trip_request,
        "budget_plan": budget_plan,
        "messages": [
            SystemMessage(content=("Validated canonical trip request:\n"
                    + json.dumps(
                        {
                            "trip_request": trip_request,
                            "budget_plan": budget_plan,
                        },indent=2,default=str,)
                )
            )
        ],
    }