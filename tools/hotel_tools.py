import json
import requests
import regex as re
from datetime import datetime, timedelta
from typing import Optional
from langchain_core.tools import tool
from Config.settings import CLEANED_RAPIDAPI_KEY

@tool
def search_location(city_name: str) -> str:
    """Look up one best destination id and type for a city."""
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    params = {"query": city_name, "locale": "en-gb"}
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        "Content-Type": "application/json",
    }
 
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("data", [])
    except Exception as e:
        return json.dumps({"error": f"Location API error: {str(e)}"})
 
    if not data:
        return json.dumps({"error": f"No location match found for {city_name}"})
 
    best = data[0]
     
    return json.dumps({
        "city": city_name,
        "dest_id": best.get("dest_id"),
        "dest_type": best.get("search_type") or best.get("dest_type")
    })

@tool
def search_hotel(
    dest_id: str,
    dest_type: str,
    checkin: Optional[str] = None,
    travelers: int = 1,
    checkout: Optional[str] = None,
    budget: Optional[float] = None,
) -> str:
    """Search hotels. budget is the maximum TOTAL room/stay price returned by the API."""
    if not dest_id or not dest_type:
        return json.dumps({"error": "dest_id and dest_type are required"})
    if not checkin:
        return json.dumps({"error": "Missing checkin date for hotel search"})

    try:
        checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
        if checkout:
            checkout_dt = datetime.strptime(checkout, "%Y-%m-%d")
            if checkout_dt <= checkin_dt:
                return json.dumps({"error": "checkout must be after checkin"})
        else:
            checkout_dt = checkin_dt + timedelta(days=1)
            checkout = checkout_dt.strftime("%Y-%m-%d")
    except ValueError:
        return json.dumps({"error": "Hotel dates must use YYYY-MM-DD"})

    try:
        travelers = max(int(travelers), 1)
    except (TypeError, ValueError):
        travelers = 1

    try:
        budget = float(budget) if budget is not None else None
    except (TypeError, ValueError):
        return json.dumps({"error": "Hotel budget must be numeric"})

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    params = {
        "dest_id": str(dest_id),
        "search_type": str(dest_type).upper(),
        "arrival_date": checkin,
        "departure_date": checkout,
        "adults": travelers,
        "room_qty": 1,
        "units": "metric",
        "temperature_unit": "c",
        "languagecode": "en-gb",
        "currency_code": "INR",
    }
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Hotel API request failed: {exc}"})
    except ValueError:
        return json.dumps({"error": "Hotel API returned invalid JSON"})
    except Exception as exc:
        return json.dumps({"error": f"Unexpected hotel API error: {exc}"})

    if not isinstance(data, dict):
        return json.dumps({"error": "Hotel API returned an unexpected response format"})

    api_data = data.get("data") or {}
    hotels = api_data.get("hotels") or []
    if not isinstance(hotels, list):
        return json.dumps({"error": "Hotel API hotels field is not a list"})

    cleaned = []
    for hotel in hotels:
        if not isinstance(hotel, dict):
            continue
        prop = hotel.get("property") or {}
        breakdown = prop.get("priceBreakdown") or {}
        gross = breakdown.get("grossPrice") or {}
        actual_price = gross.get("value")

        try:
            actual_price = float(actual_price) if actual_price is not None else None
        except (TypeError, ValueError):
            actual_price = None

        if actual_price is None:
            label = str(hotel.get("accessibilityLabel") or "")
            match = re.search(r"(?:Current price|price)[^\d]*([\d,]+(?:\.\d+)?)", label, re.I)
            if match:
                try:
                    actual_price = float(match.group(1).replace(",", ""))
                except ValueError:
                    pass

        if budget is not None and (actual_price is None or actual_price > budget):
            continue

        cleaned.append({
            "name": prop.get("name", "Unknown Hotel"),
            "rating": prop.get("reviewScore", 0),
            "rating_word": prop.get("reviewScoreWord", "N/A"),
            "price_inr": actual_price if actual_price is not None else "N/A",
            "hotel_class": prop.get("propertyClass", "N/A"),
            "checkin_from": (prop.get("checkin") or {}).get("fromTime", "N/A"),
            "checkout_until": (prop.get("checkout") or {}).get("untilTime", "N/A"),
        })

    return json.dumps({
        "dest_id": str(dest_id),
        "dest_type": str(dest_type),
        "checkin": checkin,
        "checkout": checkout,
        "budget_total_stay": budget,
        "price_semantics": "gross room/stay price as returned by the API",
        "results": cleaned[:10],
    }, indent=2)