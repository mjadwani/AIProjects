from langgraph.graph import StateGraph,START,END
from typing import TypedDict


class SubagentState(TypedDict):
    operation : str
    a : int
    squared : int
    


def square_node(state : SubagentState):
    return { 'squared' : state['a'] **2  }

Subagent = StateGraph(SubagentState)

Subagent.add_node("square_node",square_node)
Subagent.add_edge(START,"square_node")
Subagent.add_edge("square_node",END)

square_agent = Subagent.compile()

# print(square_agent.get_graph().draw_mermaid())