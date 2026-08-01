from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition


from Schema.state import MessagesState
from agents.planner import planner
from agents.assistant import assistant
from agents.enrichment import enrichment_curator
from tools.flight_tools import search_flights
from tools.hotel_tools import search_location, search_hotel

tools = [search_flights, search_location, search_hotel]
tool_node = ToolNode(tools)

builder = StateGraph(MessagesState)
builder.add_node("planner", planner)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("enrichment", enrichment_curator)

builder.add_edge(START, "planner")
builder.add_edge("planner", "assistant")

builder.add_conditional_edges(
    "assistant",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "enrichment",
    }
)

builder.add_edge("tools", "assistant")
builder.add_edge("enrichment", END)

graph = builder.compile()