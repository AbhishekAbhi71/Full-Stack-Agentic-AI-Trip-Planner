from langchain_core.messages import HumanMessage
from graph.workflow import graph

if __name__ == "__main__":
    user_query = "plan a trip from delhi to mumbai for 3 days under 20000 on 03 August 2026"

    result = graph.invoke(
        {"messages": [HumanMessage(content=user_query)]},
        {"recursion_limit": 30}
    )

    print("\n--- ✨ TRIPS ENGINE RESULTS ✨ ---\n")
    if result.get("messages"):
        print(result["messages"][-1].content)