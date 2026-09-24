import json
from datetime import datetime, timedelta
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
    AIMessage,
)
from graph.state import MessagesState

def _latest_user_text(state: MessagesState) -> str:
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            return str(msg.content).strip()
    return ""

def _tool_results(state: MessagesState) -> dict:
    """Collect tool names/results already attempted in the current graph run."""
    results = {}
    for msg in state.get("messages", []):
        if isinstance(msg, ToolMessage):
            try:
                content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
            except (TypeError, json.JSONDecodeError):
                content = {"error": str(msg.content)}
            results[msg.name] = content
    return results

def assistant(state: MessagesState):
    """Deterministic search orchestrator.

    The LLM extracts the request; this node controls tool order so a hotel search
    can never run before its destination lookup has completed.
    """
    trip_request = state.get("trip_request", {})
    budget_plan = state.get("budget_plan", {})
    user_text = _latest_user_text(state).lower()

    origin = trip_request.get("origin")
    destination = trip_request.get("destination")
    departure_date = trip_request.get("departure_date")
    return_date = trip_request.get("return_date")
    trip_type = trip_request.get("trip_type", "oneway")
    travelers = max(int(trip_request.get("travelers", 1) or 1), 1)

    wants_flight = (
        any(k in user_text for k in ("flight", "fly", "airfare", "air ticket", "plane"))
        or (origin and destination and "hotel only" not in user_text and "hotel-only" not in user_text)
    )
    wants_hotel = (
        any(k in user_text for k in ("hotel", "stay", "accommodation", "room"))
        or ("plan a trip" in user_text and origin and destination)
        or ("trip" in user_text and origin and destination and "flight only" not in user_text)
    )

    needs_live_search = wants_flight or wants_hotel
    missing = []
    if needs_live_search and not destination:
        missing.append("destination city")
    if (wants_flight or wants_hotel) and not departure_date:
        missing.append("departure date")
    if wants_flight and not origin:
        missing.append("origin city")
    if trip_type == "roundtrip" and wants_flight and not return_date:
        missing.append("return date")

    if missing:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I need the following information before I can run the live search: "
                        + ", ".join(missing)
                        + "."
                    )
                )
            ]
        }
        
    try:
        dep_dt = datetime.strptime(departure_date, "%Y-%m-%d")
        if return_date:
            checkout = return_date
        else:
            checkout = (
                dep_dt + timedelta(days=max(int(trip_request.get("trip_days", 1)) - 1, 1))
            ).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return {"messages": [AIMessage(content="The date format is invalid. Please use YYYY-MM-DD.")]}
 
    pp_flight_budget = (
        budget_plan.get("per_person_breakdown", {}).get("flight_budget")
    )
    group_hotel_budget = budget_plan.get("group_breakdown", {}).get("hotel_budget")

    attempted = _tool_results(state)
    tool_calls = []
    
    if wants_flight:
        flight_tool_name = (
            "search_roundtrip_flights" if trip_type == "roundtrip"
            else "search_oneway_flights"
        )
        if flight_tool_name not in attempted:
            args = {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "travelers": travelers,
                "max_budget": pp_flight_budget,
            }
            if trip_type == "roundtrip":
                args["return_date"] = return_date
            tool_calls.append({
                "name": flight_tool_name,
                "args": args,
                "id": f"{flight_tool_name}_1",
                "type": "tool_call",
            })

    location_data = attempted.get("search_location")
    if wants_hotel and "search_location" not in attempted:
        tool_calls.append({
            "name": "search_location",
            "args": {"city_name": destination},
            "id": "search_location_1",
            "type": "tool_call",
        })
    elif wants_hotel and "search_hotel" not in attempted:
        if isinstance(location_data, dict) and not location_data.get("error"):
            dest_id = location_data.get("dest_id")
            dest_type = location_data.get("dest_type")
            if dest_id and dest_type:
                tool_calls.append({
                    "name": "search_hotel",
                    "args": {
                        "dest_id": str(dest_id),
                        "dest_type": str(dest_type),
                        "checkin": departure_date,
                        "checkout": checkout,
                        "travelers": travelers,
                        "budget": group_hotel_budget,
                    },
                    "id": "search_hotel_1",
                    "type": "tool_call",
                })

    if tool_calls:
        return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}

    return {"messages": [AIMessage(content="Search data collected. Preparing your trip summary...")]}