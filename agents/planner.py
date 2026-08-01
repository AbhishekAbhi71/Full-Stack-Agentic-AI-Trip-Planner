import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model

from Config.settings import CLEANED_GEMINI_KEY
from Schema.models import TripRequest
from Schema.state import MessagesState
from utils.date_utils import normalize_date
from utils.budget_utils import allocate_budget

llm = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    api_key=CLEANED_GEMINI_KEY
)

planner_llm = llm.with_structured_output(TripRequest)

def planner(state: MessagesState):
    user_text = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_text = msg.content
            break

    system_prompt = """
    Extract travel request fields from the user message.
    
    Rules:
    - Identify origin and destination cities.
    - Extract total budget if the user gave one overall trip budget.
    - Extract trip_days if the user mentioned duration like 3 days.
    - Extract departure_date if available and normalize later.
    - If travel style is not stated, use balanced.
    - Return only structured fields.
    """
    
    parsed = planner_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_text)
        ])
    
    trip_request = parsed.model_dump()
    trip_request["departure_date"] = normalize_date(trip_request.get("departure_date"))
    
    budget_plan = allocate_budget(
            total_budget=trip_request.get("total_budget"),
            trip_days=trip_request.get("trip_days", 1),
            travel_style=trip_request.get("travel_style", "balanced"),
        )
    
    summary = {
            "trip_request": trip_request,
            "budget_plan": budget_plan
        }
    
    return {
            "trip_request": trip_request,
            "budget_plan": budget_plan,
            "messages": [
                SystemMessage(
                    content=f"Structured planning context:\n{json.dumps(summary, indent=2)}"
                )
            ],
        }