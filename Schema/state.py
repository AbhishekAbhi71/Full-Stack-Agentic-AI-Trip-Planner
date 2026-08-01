from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class MessagesState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    trip_request: dict
    budget_plan: dict
