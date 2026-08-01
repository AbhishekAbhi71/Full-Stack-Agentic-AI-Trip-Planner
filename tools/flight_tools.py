import json
import requests
from langchain_core.tools import tool
from Config.settings import CLEANED_RAPIDAPI_KEY

@tool
def search_flights(origin: str, destination: str, max_budget: float, departure_date: str) -> str:
    """Search flights between two cities under a user budget."""
    url = "https://skyscanner-flights4.p.rapidapi.com/api/v1/search"
    querystring = {
        "origin": origin,
        "destination": destination,
        "limit": "20",
        "adults": "1",
        "date": departure_date,
        "currency": "INR",
        "cabin": "economy",
        "market": "US",
        "locale": "en-US",
    }
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "skyscanner-flights4.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return json.dumps({"error": f"Flight API error: {str(e)}"})

    flights = data.get("results", [])
    if not flights:
        return json.dumps({
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "results": []
        })

    filtered = []
    for flight in flights:
        price_raw = flight.get("price_raw")
        if price_raw is None or price_raw > max_budget:
            continue

        leg = flight.get("legs", [{}])[0]
        carriers = flight.get("carriers", [])
        airline = carriers[0] if carriers else "Unknown Airline"

        filtered.append({
            "airline": airline,
            "departure": leg.get("dep", "Unknown"),
            "arrival": leg.get("arr", "Unknown"),
            "duration_min": leg.get("dur_min", "N/A"),
            "stops": leg.get("stops", 0),
            "price_inr": price_raw,
        })

    filtered = sorted(filtered, key=lambda x: x["price_inr"])[:5]

    return json.dumps({
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "max_budget": max_budget,
        "results": filtered,
    }, indent=2)
