import json
from langchain_core.messages import (
    ToolMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.config import get_stream_writer
from langchain.chat_models import init_chat_model
from Config.settings import CLEANED_GEMINI_KEY
from Prompt.travel_prompts import build_enrichment_prompt

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    api_key=CLEANED_GEMINI_KEY,
)

def enrichment_curator(state):

    flights = []
    hotels = []
    origin_city = None
    destination_city = None
    trip_req = state.get("trip_request",{})
    budget_plan = state.get("budget_plan",{})
    travelers = max(trip_req.get("travelers", 1) or 1,1)
    trip_days = max(trip_req.get("trip_days", 1) or 1,1)
    group_total_budget = (
        budget_plan.get("group_total_budget",0)
    )
    group_bd = budget_plan.get("group_breakdown",{})
    per_person_bd = budget_plan.get("per_person_breakdown",{})
    group_food = group_bd.get("food_budget",0)
    group_local = group_bd.get("local_transport_budget",0)
    group_other = group_bd.get("other_budget", 0)
    pp_food = per_person_bd.get( "food_budget",0)
    pp_local = per_person_bd.get("local_transport_budget",0)
    pp_other = per_person_bd.get("other_budget",0)

    for msg in state.get("messages", []):
        if isinstance(msg, ToolMessage):
            try:
                if isinstance(msg.content,str):
                    data = json.loads(msg.content)
                elif isinstance(msg.content,dict):
                    data = msg.content
                else:
                    continue
            except Exception:
                continue
            
            if msg.name in ["search_oneway_flights","search_roundtrip_flights"]:
                flights = data.get("results",[])
                origin_city = (data.get("origin")or origin_city)
                destination_city = (data.get("destination")or destination_city)
                
            elif msg.name == "search_hotel":
                hotels = data.get("results",[])

    flights = [
        f for f in flights
        if isinstance(f.get("price_inr"),(int, float))
    ]

    hotels = [
        h for h in hotels
        if isinstance(h.get("price_inr"),(int, float))
    ]

    flights_sorted = sorted(flights,key=lambda x: x["price_inr"])
    
    hotels_sorted = sorted(hotels,key=lambda x: x["price_inr"])
    
    cheapest_flight = (flights_sorted[0]
        if flights_sorted
        else None
    )

    cheapest_hotel = (hotels_sorted[0]
        if hotels_sorted
        else None
    )

    for hotel in hotels_sorted:
        try:
            rating = float(hotel.get("rating",0)or 0)
            price = float(hotel["price_inr"])
            hotel["value_score"] = round((rating ** 2) / price,6) if price > 0 else 0
        except Exception:
            hotel["value_score"] = 0

    best_value_hotel = max(hotels_sorted,
            key=lambda x: x.get(
            "value_score",
            0
        ),
        default=None
    )

    selected_flight_price = (
        float(cheapest_flight["price_inr"])
        if cheapest_flight
        else 0.0
    )

    selected_hotel_price = (
        float(cheapest_hotel["price_inr"])
        if cheapest_hotel
        else 0.0
    )

    group_flight_spend = round(selected_flight_price* travelers,2)
    group_hotel_spend = round(selected_hotel_price,2)
    group_food_spend = float(group_food or 0)
    group_local_spend = float(group_local or 0)
    group_other_spend = float(group_other or 0)
    group_total_spend = round(
        group_flight_spend
        + group_hotel_spend
        + group_food_spend
        + group_local_spend
        + group_other_spend,
        2,
    )

    remaining_budget = (
        round(float(group_total_budget)- group_total_spend,2)
        if group_total_budget is not None
        else None
    )

    payload = {
        "origin_city":origin_city or trip_req.get("origin"),
        "destination_city":destination_city or trip_req.get("destination"),
        "trip_request":trip_req,
        "budget_plan":budget_plan,
        "travelers":travelers,
        "trip_days":trip_days,
        "all_flights":flights_sorted,
        "all_hotels":hotels_sorted,
        "recommendations": {
            "cheapest_flight":cheapest_flight,
            "cheapest_hotel":cheapest_hotel,
            "best_value_hotel":best_value_hotel,
        },
        "computed_costs": {
            "selected_flight_price_per_person":selected_flight_price,
            "selected_hotel_price_total_stay":selected_hotel_price,
            "group_flight_spend":group_flight_spend,
            "group_hotel_spend":group_hotel_spend,
            "group_food_spend":group_food_spend,
            "group_local_transport_spend":group_local_spend,
            "group_other_spend":group_other_spend,
            "group_total_spend":group_total_spend,
            "remaining_budget":remaining_budget,
            "per_person_total_spend":round(group_total_spend/ travelers,2),
        },
    }
    system_prompt = build_enrichment_prompt(
        origin_city=(origin_city or trip_req.get("origin")),
        destination_city=( destination_city or trip_req.get("destination")),
        trip_days=trip_days,
        travelers=travelers,
        group_total_budget=group_total_budget,
        group_food=group_food,
        pp_food=pp_food,
        group_local=group_local,
        pp_local=pp_local,
        group_other=group_other,
        pp_other=pp_other,
    )
 
    writer = get_stream_writer()
    full_response = ""
    for chunk in llm.stream([
        SystemMessage(content=system_prompt),
        HumanMessage(content=json.dumps(payload,indent=2,default=str))
    ]):

        if chunk.content:
            full_response += chunk.content
            writer(chunk.content)
 
    return {
        "messages": [AIMessage(content=full_response)]
    }