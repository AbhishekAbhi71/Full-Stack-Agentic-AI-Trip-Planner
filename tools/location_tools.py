import json
import requests
from langchain_core.tools import tool
from Config.settings import CLEANED_RAPIDAPI_KEY

@tool
def search_location(city_name: str) -> str:
    """Look up the best Booking.com destination id/type for a city."""
    if not city_name:
        return json.dumps({"error": "city_name is required"})

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    params = {"query": city_name, "locale": "en-gb"}
    headers = {
        "x-rapidapi-key": CLEANED_RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Location API request failed: {exc}"})
    except ValueError:
        return json.dumps({"error": "Location API returned invalid JSON"})
    except Exception as exc:
        return json.dumps({"error": f"Unexpected location API error: {exc}"})

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        return json.dumps({"error": f"No location match found for {city_name}"})

    best = next((item for item in data if isinstance(item, dict)), None)
    if not best:
        return json.dumps({"error": f"No valid location match found for {city_name}"})

    dest_id = best.get("dest_id")
    dest_type = best.get("search_type") or best.get("dest_type")
    if not dest_id or not dest_type:
        return json.dumps({"error": f"Location result for {city_name} lacks dest_id/dest_type"})

    return json.dumps({
        "city": city_name,
        "dest_id": dest_id,
        "dest_type": dest_type,
    })
