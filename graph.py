from typing import Literal

from langgraph.graph import StateGraph, END

from state import State
from agents import (
    product_manager,
    programmer,
    code_reviewer,
    tester,
    fix_code,
)


def _route_after_review(state: State) -> Literal["fix_code", "test"]:
    return "test" if state["review_passed"] else "fix_code"


def build_agent_graph():
    graph = StateGraph(State)

    graph.add_node("product_manager", product_manager)
    graph.add_node("programmer", programmer)
    graph.add_node("code_reviewer", code_reviewer)
    graph.add_node("tester", tester)
    graph.add_node("fix_code", fix_code)

    graph.set_entry_point("product_manager")

    graph.add_edge("product_manager", "programmer")
    graph.add_edge("programmer", "code_reviewer")

    graph.add_conditional_edges(
        "code_reviewer",
        _route_after_review,
        {"test": "tester", "fix_code": "fix_code"},
    )

    graph.add_edge("fix_code", "code_reviewer")
    graph.add_edge("tester", END)

    return graph.compile()
