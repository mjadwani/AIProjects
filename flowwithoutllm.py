from langgraph.graph import START,END,StateGraph
from typing import TypedDict
from langchain_community.tools import DuckDuckGoSearchResults
from subagent import Subagent,square_agent
from langchain.messages import AIMessage,HumanMessage
# from langchain_core.tools import tool



# @tool


class DefState(TypedDict):
    a : int
    b : int
    query : HumanMessage
    operation : str
    oper_sum : int
    oper_mult : int
    oper_square : int
    search_result : AIMessage
    
def search_tool(state : DefState) :
    # query = "Capital Of India"
    srch = DuckDuckGoSearchResults()
    result = srch.invoke(state['query'])
    
    return {"search_result" : AIMessage(content=result)}

def which_operation(state : DefState):
    # print("which_operation\n",state)
    # state['operation'] = state['operation']
    return {"operation" : state["operation"]}

def my_router(state : DefState) :
    if state['operation'] == "sum" :
        return "sum"
    if state['operation'] == "multiply" :
        return "multiply"
    if state['operation'] == "search" :
        return "search"
    if state["operation"] == "square" :
        return "square_agent_node"
        # response = square_agent.invoke({ "operation" : state["operation"],
        #                                     "a" :state['a'],
        #                                     "square" : 0})
        # print(response)
        # return "END"          
    return "No Operation Specified"

def sum(state : DefState):
    return {'oper_sum':state['a'] + state['b']}


def multiply(state : DefState):
    return {'oper_mult' : state['a'] * state['b']}

def square_agent_node(state : DefState):
    response = square_agent.invoke({ "operation" : state["operation"],
                                            "a" :state['a'],
                                            "squared" : 0})
    return {"oper_square" : response['squared']}
operflow = StateGraph(DefState)

operflow.add_node("which_operation",which_operation)
operflow.add_node("sum",sum)
operflow.add_node("multiply",multiply)
operflow.add_node("search_tool",search_tool)
operflow.add_node("square_agent_node",square_agent_node)

operflow.add_edge(START,"which_operation")
operflow.add_conditional_edges("which_operation",my_router,
                               {
                                   "sum" : "sum",
                                   "multiply" : "multiply",
                                   "search" : "search_tool" ,
                                   "square_agent_node" : "square_agent_node" ,
                                   "No Operation Specified" : END
                               })

operflow.add_edge("sum",END)
operflow.add_edge("multiply",END)
operflow.add_edge("search_tool",END)
operflow.add_edge("square_agent_node",END)

agent = operflow.compile()

# print(agent.get_graph().draw_mermaid())
# user_input= HumanMessage(content="Capital of India")
# init_state = {
#     "a" : 5,
#     "b" : 10,
#     "query" : user_input.content ,
#     "operation" : "search" ,
#     "oper_sum" : 0,
#     "oper_mult" : 0,
#     "oper_square " : 0,
#     "search_result" : AIMessage(content=" ")
# }

# # result = agent.invoke(init_state)

# # print(result)

# # /quit


# # result = agent.stream(init_state)

# for chunk in agent.stream(init_state) :
    
#     # print(chunk.items())
#     for nodename , stat_update in chunk.items():
#         print(f"----from {nodename}----")
#         print(f"following state got updated {stat_update}")
    # print("hello\n")
