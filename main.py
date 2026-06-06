"""Multi-agent code generation pipeline using LangGraph.

Agents: Product Manager → Programmer → Code Reviewer ⇄ Fix → Tester
"""

from graph import build_agent_graph
from state import initial_state


def run(requirement: str) -> dict:
    app = build_agent_graph()

    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  🤖  Multi-Agent Code Generation System".ljust(54) + "║")
    print("╠" + "═" * 58 + "╣")
    for line in requirement.strip().split("\n"):
        print("║" + f"  📝  {line.strip()}".ljust(54) + "║")
    print("╚" + "═" * 58 + "╝")

    # LangGraph stream: yields {node_name: state} as each node completes
    final_state = {}
    for chunk in app.stream(initial_state(requirement)):
        final_state.update(next(iter(chunk.values())))

    print("\n" + "═" * 60)
    print("  📦  FINAL CODE")
    print("═" * 60)
    print(final_state.get("code", ""))
    print("═" * 60)
    print("  🎉  Pipeline Complete\n")

    return final_state


if __name__ == "__main__":
    run("""
    写一个函数，判断一个数字是否为质数。
    输入：整数
    输出：布尔值 True/False
    """)
