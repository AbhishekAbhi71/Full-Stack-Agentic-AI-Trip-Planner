import json
import regex as re
from datetime import datetime, timedelta
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
)
from langchain.chat_models import init_chat_model
from Config.settings import CLEANED_GEMINI_KEY
from models.Trip_models import TripRequest
from utils.date_utils import normalize_date
from utils.budget_utils import allocate_budget
from graph.state import MessagesState

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    api_key=CLEANED_GEMINI_KEY,
)

planner_llm = llm.with_structured_output(TripRequest)

def planner(state: MessagesState):
    user_text = ""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            user_text = msg.content
            break
        
    system_prompt = """
Extract travel request fields from the user message matching the TripRequest schema.

Fields to extract:
- origin: Starting city or null (Do NOT invent a city)
- destination: Destination city
- departure_date: Date in "YYYY-MM-DD" format or null
- return_date: Date in "YYYY-MM-DD" format or null
- trip_days: Number of days for the trip (e.g. "3 days" → 3; Default: 1)
- total_budget: Overall trip budget in INR (If not mentioned, set to null)
- travel_style: "budget", "balanced", or "comfort" (Default: "balanced")
- trip_type: "oneway" or "roundtrip" (Default: "oneway")
- travelers: Number of people traveling (Default: 1)

Edge cases:
- If origin is missing, set to null.
- If no budget is mentioned, set total_budget to null.
- If departure date is not specified, leave as null.
- Extract travelers if mentioned (e.g., "for 3 people" → travelers=3). Default to 1.

Examples:

User: "I need flights from Delhi to Goa on 10 Sept, budget 15k, 3 days, budget style."
→ origin="Delhi", destination="Goa", departure_date="2026-09-10", return_date=null, total_budget=15000, trip_days=3, travel_style="budget", trip_type="oneway", travelers=1

User: "I need flights from Delhi to Goa on 10 Sept and return on 20 sep, budget 25k, 3 days, budget style."
→ origin="Delhi", destination="Goa", departure_date="2026-09-10", return_date="2026-09-20", total_budget=25000, trip_days=3, travel_style="budget", trip_type="roundtrip", travelers=1

User: "I want to go to Goa from patna for 3 days on 23 Aug"
→ origin="patna", destination="Goa", departure_date="2026-08-23", return_date=null, total_budget=null, trip_days=3, travel_style="balanced", trip_type="oneway", travelers=1

User: "Plan a trip from Patna to Bangalore, 4 days, total 25k, balanced."
→ origin="Patna", destination="Bangalore", departure_date=null, return_date=null, total_budget=25000, trip_days=4, travel_style="balanced", trip_type="oneway", travelers=1
"""

    parsed = planner_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_text)
    ])
 
    trip_request = parsed.model_dump()
    raw_text = str(user_text).strip()
    text_lower = raw_text.lower()

    route_match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)"
        r"(?=\s+(?:for|under|below|within|on|with|budget|"
        r"round[\s-]?trip|one[\s-]?way)\b|$)",
        raw_text,
        re.IGNORECASE,
    )
    if route_match:
        trip_request["origin"] = route_match.group(1).strip(" ,.")
        trip_request["destination"] = route_match.group(2).strip(" ,.")

    traveler_match = re.search(
        r"\b(?:for|with)\s+(\d+)\s+"
        r"(?:people|persons|person|travelers|travellers)\b",
        text_lower,
    )
    if traveler_match:
        trip_request["travelers"] = int(traveler_match.group(1))

    days_match = re.search(r"\bfor\s+(\d+)\s+days?\b", text_lower)
    if days_match:
        trip_request["trip_days"] = int(days_match.group(1))

    budget_match = re.search(
        r"\b(?:under|below|within)\s+"
        r"(?:inr|rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        text_lower,
    )
    if budget_match:
        trip_request["total_budget"] = float(
            budget_match.group(1).replace(",", "")
        )

    if re.search(r"\bround[\s-]?trip\b", text_lower):
        trip_request["trip_type"] = "roundtrip"
    elif re.search(r"\bone[\s-]?way\b", text_lower):
        trip_request["trip_type"] = "oneway"

    date_candidates = re.findall(
        r"\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b",
        raw_text,
        re.IGNORECASE,
    )
    if date_candidates:
        normalized_first = normalize_date(date_candidates[0])
        if normalized_first:
            trip_request["departure_date"] = normalized_first

        if len(date_candidates) >= 2:
            normalized_second = normalize_date(date_candidates[1])
            if normalized_second:
                trip_request["return_date"] = normalized_second
                trip_request["trip_type"] = "roundtrip"

    trip_request["departure_date"] = normalize_date(trip_request.get("departure_date"))
    trip_request["return_date"] = normalize_date(trip_request.get("return_date"))

    if trip_request.get("return_date") or trip_request.get("trip_type") == "roundtrip":
        trip_request["trip_type"] = "roundtrip"
        if not trip_request.get("return_date") and trip_request.get("departure_date"):
            try:
                dep_dt = datetime.strptime(trip_request["departure_date"], "%Y-%m-%d")
                days = trip_request.get("trip_days", 1)
                trip_request["return_date"] = (dep_dt + timedelta(days=days)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass
    else:
        trip_request["trip_type"] = "oneway"
   
    if trip_request.get("departure_date") and trip_request.get("return_date"):
        try:
            dep = datetime.strptime(trip_request["departure_date"], "%Y-%m-%d").date()
            ret = datetime.strptime(trip_request["return_date"], "%Y-%m-%d").date()
            if ret <= dep:
                raise ValueError("return date must be after departure date")
            trip_request["trip_days"] = (ret - dep).days + 1
        except ValueError as exc:
            return {"messages": [AIMessage(content=f"Invalid trip dates: {exc}. Please provide valid dates.")]}

    budget_plan = allocate_budget(
        total_budget=trip_request.get("total_budget"),
        trip_days=trip_request.get("trip_days", 1),
        travelers=trip_request.get("travelers", 1),
        travel_style=trip_request.get("travel_style", "balanced"),
        trip_type=trip_request.get("trip_type", "oneway")
    )

    summary = {
        "trip_request": trip_request,
        "budget_plan": budget_plan
    }

    return {
        "trip_request": trip_request,
        "budget_plan": budget_plan,
        "messages": [
            SystemMessage(content=f"Structured planning context:\n{json.dumps(summary, indent=2, default=str)}")
        ],
    }