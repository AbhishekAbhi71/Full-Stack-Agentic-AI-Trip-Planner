import json
import requests
import regex as re
from datetime import datetime, timedelta
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
def search_hotel(dest_id: str, dest_type: str, checkin: str = None, checkout: str = None, budget: float = None) -> str:
    """Search hotels in a given city using Booking.com API."""
    if not checkin:
        return json.dumps({"error": "Missing checkin date for hotel search"})

    if checkin and not checkout:
        checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
        checkout = (checkin_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    params = {
        "dest_id": dest_id,
        "search_type": dest_type.upper(),
        "arrival_date": checkin,
        "departure_date": checkout,
        "adults": 2,
        "room_qty": 1,
        "units": "metric",
        "temperature_unit": "c",
        "languagecode": "en-gb",
        "currency_code": "INR",
    }

    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    try:
        hotel_response = requests.get(url, headers=headers, params=params, timeout=30)
        hotel_response.raise_for_status()
        data = hotel_response.json()
    except Exception as e:
        return json.dumps({"error": f"Hotel API error: {str(e)}"})

    api_data_block = data.get("data", {})
    hotels = api_data_block.get("hotels", [])

    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    if budget is not None:
        filtered_hotels = []
        for h in hotels:
            property_data = h.get("property", {})
            price_breakdown = property_data.get("priceBreakdown", {})
            gross_price = price_breakdown.get("grossPrice", {})
            actual_price = gross_price.get("value")

            if actual_price is None:
                label = h.get("accessibilityLabel", "")
                match = re.search(r"Current price (\d+)", label)
                if match:
                    actual_price = float(match.group(1))

            if actual_price is None:
                actual_price = float("inf")

            if actual_price <= budget:
                filtered_hotels.append(h)

        hotels = filtered_hotels

    cleaned_hotels = []
    for h in hotels:
        property_data = h.get("property", {})
        cleaned_hotels.append({
            "name": property_data.get("name", "Unknown Hotel"),
            "rating": property_data.get("reviewScore", "N/A"),
            "rating_word": property_data.get("reviewScoreWord", "N/A"),
            "price_inr": property_data.get("priceBreakdown", {}).get("grossPrice", {}).get("value", "N/A"),
            "hotel_class": property_data.get("propertyClass", "N/A"),
            "checkin_from": property_data.get("checkin", {}).get("fromTime", "N/A"),
            "checkout_until": property_data.get("checkout", {}).get("untilTime", "N/A"),
        })

    return json.dumps({
        "dest_id": dest_id,
        "dest_type": dest_type,
        "checkin": checkin,
        "checkout": checkout,
        "budget": budget,
        "results": cleaned_hotels[:10]
    }, indent=2)