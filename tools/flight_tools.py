import json
import requests
from datetime import datetime
from typing import Optional
from langchain_core.tools import tool
from Config.settings import CLEANED_RAPIDAPI_KEY

@tool
def search_oneway_flights(
    origin: str,
    destination: str,
    departure_date: str,
    max_budget: Optional[float] = None,
    travelers: int = 1,
) -> str:
    """Search one-way flights. max_budget is a per-person budget."""
    if not origin or not destination or not departure_date:
        return json.dumps({"error": "origin, destination and departure_date are required"})
    try:
        travelers = max(int(travelers), 1)
    except (TypeError, ValueError):
        travelers = 1

    url = "https://skyscanner-flights4.p.rapidapi.com/api/v1/search"
    params = {
        "origin": origin,
        "destination": destination,
        "limit": "20",
        "adults": str(travelers),
        "date": departure_date,
        "currency": "INR",
        "cabin": "economy",
        "market": "US",
        "locale": "en-US",
    }
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "skyscanner-flights4.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Flight API request failed: {exc}"})
    except ValueError:
        return json.dumps({"error": "Flight API returned invalid JSON"})
    except Exception as exc:
        return json.dumps({"error": f"Unexpected flight API error: {exc}"})

    if not isinstance(data, dict):
        return json.dumps({"error": "Flight API returned an unexpected response format"})

    flights = data.get("results") or []
    if not isinstance(flights, list):
        return json.dumps({"error": "Flight API results field is not a list"})

    filtered = []
    for flight in flights:
        if not isinstance(flight, dict):
            continue
        try:
            price = float(flight.get("price_raw"))
        except (TypeError, ValueError):
            continue
        if max_budget is not None and price > float(max_budget):
            continue

        legs = flight.get("legs") or [{}]
        leg = legs[0] if isinstance(legs[0], dict) else {}
        carriers = flight.get("carriers") or []
        airline = carriers[0] if carriers else "Unknown Airline"

        filtered.append({
            "airline": airline,
            "departure": leg.get("dep", "Unknown"),
            "arrival": leg.get("arr", "Unknown"),
            "duration_min": leg.get("dur_min", "N/A"),
            "stops": leg.get("stops", 0),
            "price_inr": price,
        })

    return json.dumps({
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "max_budget_per_person": max_budget,
        "results": sorted(filtered, key=lambda x: x["price_inr"])[:5],
    }, indent=2)


@tool
def search_roundtrip_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int = 1,
    max_budget: Optional[float] = None,
) -> str:
    """Search round-trip flights. max_budget is a per-person budget."""
    if not all((origin, destination, departure_date, return_date)):
        return json.dumps({"error": "origin, destination, departure_date and return_date are required"})
    try:
        dep = datetime.strptime(departure_date, "%Y-%m-%d")
        ret = datetime.strptime(return_date, "%Y-%m-%d")
        if ret <= dep:
            return json.dumps({"error": "return_date must be after departure_date"})
    except ValueError:
        return json.dumps({"error": "Flight dates must use YYYY-MM-DD"})

    try:
        travelers = max(int(travelers), 1)
    except (TypeError, ValueError):
        travelers = 1

    url = "https://skyscanner-flights4.p.rapidapi.com/api/v1/roundtrip"
    params = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "adults": str(travelers),
        "currency": "INR",
    }
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "skyscanner-flights4.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Flight API request failed: {exc}"})
    except ValueError:
        return json.dumps({"error": "Flight API returned invalid JSON"})
    except Exception as exc:
        return json.dumps({"error": f"Unexpected flight API error: {exc}"})

    if not isinstance(data, dict):
        return json.dumps({"error": "Flight API returned an unexpected response format"})

    results = []
    for flight in data.get("results") or []:
        if not isinstance(flight, dict):
            continue
        try:
            price = float(flight.get("price_raw"))
        except (TypeError, ValueError):
            continue
        if max_budget is not None and price > float(max_budget):
            continue

        carriers = flight.get("carriers") or []
        legs = flight.get("legs") or []
        outbound = legs[0] if len(legs) > 0 and isinstance(legs[0], dict) else {}
        inbound = legs[1] if len(legs) > 1 and isinstance(legs[1], dict) else {}

        results.append({
            "airline": carriers[0] if carriers else "Unknown Airline",
            "price_inr": price,
            "departure": outbound.get("dep", departure_date),
            "arrival": outbound.get("arr", "N/A"),
            "outbound_stops": outbound.get("stops", 0),
            "return_departure": inbound.get("dep", return_date),
            "return_arrival": inbound.get("arr", "N/A"),
            "return_stops": inbound.get("stops", 0),
            "trip_type": "roundtrip",
        })

    return json.dumps({
        "trip_type": "roundtrip",
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "max_budget_per_person": max_budget,
        "results": sorted(results, key=lambda x: x["price_inr"])[:5],
    }, indent=2)
