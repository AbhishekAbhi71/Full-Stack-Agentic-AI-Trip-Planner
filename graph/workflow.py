from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)
from graph.state import MessagesState
from graph.planner import planner
from graph.validator import validator
from graph.assistant import assistant
from graph.enrichment import enrichment_curator
from tools import ALL_TOOLS

def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("planner",planner)
    builder.add_node("validator",validator)
    builder.add_node("assistant",assistant)
    builder.add_node("tools",ToolNode(ALL_TOOLS))
    builder.add_node("enrichment",enrichment_curator)
    
    builder.add_edge(START,"planner")
    builder.add_edge("planner","validator")
    builder.add_edge("validator","assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "enrichment",
        },
    )
    builder.add_edge("tools","assistant")
    builder.add_edge("enrichment",END)
    
    return builder.compile()