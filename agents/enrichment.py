import json
from langchain_core.messages import SystemMessage,HumanMessage,ToolMessage
from langchain.chat_models import init_chat_model

from Config.settings import CLEANED_GEMINI_KEY
from Schema.state import MessagesState
from tools.flight_tools import search_flights
from tools.hotel_tools import search_location, search_hotel

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    api_key=CLEANED_GEMINI_KEY
)

tools = [search_flights, search_location, search_hotel]
llm_with_tools = llm.bind_tools(tools)

def enrichment_curator(state: MessagesState):
    flights = []
    hotels = []
    destination_city = None

    for msg in state["messages"]:
        if isinstance(msg, ToolMessage):
            try:
                data = json.loads(msg.content)
            except Exception:
                continue

            if msg.name == "search_flights":
                flights = data.get("results", [])
                destination_city = data.get("destination") or destination_city
            elif msg.name == "search_hotel":
                hotels = data.get("results", [])

    flights = [f for f in flights if isinstance(f.get("price_inr"), (int, float))]
    hotels = [h for h in hotels if isinstance(h.get("price_inr"), (int, float))]

    flights_sorted = sorted(flights, key=lambda x: x["price_inr"]) if flights else []
    hotels_sorted = sorted(hotels, key=lambda x: x["price_inr"]) if hotels else []

    cheapest_flight = flights_sorted[0] if flights_sorted else None
    cheapest_hotel = hotels_sorted[0] if hotels_sorted else None

    for h in hotels_sorted:
        try:
            rating = float(h.get("rating") or 0)
            price = float(h["price_inr"])
            h["value_score"] = round((rating * 10) / price, 4) if price > 0 else 0
        except Exception:
            h["value_score"] = 0

    best_value_hotel = max(hotels_sorted, key=lambda x: x.get("value_score", 0), default=None) if hotels_sorted else None

    payload = {
        "destination_city": destination_city,
        "trip_request": state.get("trip_request", {}),
        "budget_plan": state.get("budget_plan", {}),
        "all_flights": flights_sorted,
        "all_hotels": hotels_sorted,
        "recommendations": {
            "cheapest_flight": cheapest_flight,
            "cheapest_hotel": cheapest_hotel,
            "best_value_hotel": best_value_hotel
        }
    }

    system_prompt = """
You are a premium travel concierge.

Use ONLY the provided structured data.

Format the response in markdown with these sections:
1. Budget Allocation
2. Flight Results
3. Hotel Results
4. Recommendations
5. Creative Micro-Itinerary
6. Budget Summary

Rules:
- Show the intelligent budget split first.
- Show every flight option under Flight Results.
- Show every hotel option under Hotel Results.
- In Recommendations, repeat only the cheapest flight, cheapest hotel, and best-value hotel.
- Show some tourist spot of the destination city
- Mention food, local transport, and other budget buckets from budget_plan even though they were not searched via tools.
- Best-value hotel means good rating relative to price, not necessarily the absolute cheapest.
- Keep the output clean and easy to scan.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=json.dumps(payload, indent=2))
    ])
    return {"messages": [response]}