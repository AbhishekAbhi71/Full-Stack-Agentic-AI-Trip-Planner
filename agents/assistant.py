import json
from langchain_core.messages import SystemMessage
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

def assistant(state: MessagesState):
    trip_request = state.get("trip_request", {})
    budget_plan = state.get("budget_plan", {})

    system_prompt = f"""
You are a travel search orchestrator.

Your only job is to collect raw search data using tools.

Structured trip request:
{json.dumps(trip_request, indent=2)}

Budget plan:
{json.dumps(budget_plan, indent=2)}

Rules:
- Do not write itinerary text.
- Do not explain results.
- First get flight results if requested or if origin and destination are present.
- For hotels, first call search_location, then call search_hotel.
- Use budget_plan.hotel_budget_per_night for hotel search (per night budget)
- Use budget_plan.hotel_budget for total trip hotel budget
- Food, local transport, and other budgets are informational and must not trigger tools.
- If the user did not specify hotel dates but gave a departure date, use the departure date as hotel check-in and the next day as checkout.
- If both valid flight and hotel results are already present in tool outputs, stop calling tools.
- If hotel results are unavailable after a valid tool call, stop and let the formatter report that clearly.
- Ask a short clarification question only if a required field is missing.
"""

    response = llm_with_tools.invoke(
        [SystemMessage(content=system_prompt)] + state["messages"]
    )
    return {"messages": [response]}