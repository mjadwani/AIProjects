from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from db2rep import func_max_min_date
from db2rep import func_accounting_by_hour_authid
from db2rep import func_accounting_by_authid
from db2rep import func_accounting_by_anyid
from langchain_core.messages import SystemMessage,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from datetime import datetime
from pydantic import BaseModel,Field
# from langchain_core.prompts import SystemMessagePromptTemplate




model = ChatOllama (model="gemma4:e4b",num_ctx=8192,temperature=0)
checkpointer = InMemorySaver()
class PRACagentState(TypedDict):
    messages : Annotated[list,add_messages]

@tool
def tool_func_max_min_date():
    '''
    this tool returns table data stats following is 
    oldest and latest timestamp recorded in the DMRACDTL table.
    number of rows in table.Use this for questions about row counts or dates.
    '''
    response = func_max_min_date()

    return {'response' : response }

@tool
def tool_accounting_by_hour_authid(db2ssid: str = "DMU1",
                                   authid: str = "BMCADM" ,
                                   inp_date: str ="05/28/2026") -> str:
    """
    Fetches the accounting metrics for Db2 profile filtered by an authid ,subsystem and date for each day . 
    Returns data indicators regarding SQL activity, lock suspensions, CPU consumption, 
    and transaction volumes.
    date format should be in mm/dd/yyyy format
    """
    # Call your original HTTP client function
    llm_ready_string = func_accounting_by_hour_authid(db2ssid=db2ssid,authid=authid,inpdate=inp_date)
    
    # Process it down into a clean, contextual summary string
    # llm_ready_string = process_db2_metrics_for_llm(raw_response)
    
    return llm_ready_string

@tool
def tool_accounting_by_authid(db2ssid: str = "DMU1",
                                   authid: str = "BMCADM" ,
                                   inp_date: str ="05/28/2026",
                                   inp_hour:str = "00" ) -> str:
    """
    Fetches the accounting information of individual thread shortlisted by 
    tool_accounting_by_hour_authid tool to identify the offending thread using maximum resource. 
    date format should be in mm/dd/yyyy format
    Returns data indicators regarding SQL activity, lock suspensions, CPU consumption, 
    and transaction volumes.
    """
    # Call your original HTTP client function
    llm_ready_string = func_accounting_by_authid(db2ssid=db2ssid,authid=authid,inpdate=inp_date,hr1=inp_hour)
    
    # Process it down into a clean, contextual summary string
    # llm_ready_string = process_db2_metrics_for_llm(raw_response)
    
    return llm_ready_string

class ContextInfo(BaseModel):
    db2ssid : str=Field(description="Db2 Subsystem Information")
    inp_date : str=Field(description="Date for which report needs to be generated")
    inp_hour : str=Field(description=" Hour for Each Day . " )

@tool(args_schema=ContextInfo)
def tool_accounting_by_anyid(db2ssid: str = "DMU1",
                                   
                                   inp_date: str ="05/28/2026",
                                   inp_hour:str = "00" ) -> str:
    
    """
    Queries the Db2 performance database to retrieve a consolidated accounting report 
    for a specific subsystem, date, and hour interval.
    
    Use this tool when the user asks for performance metrics, system health, or workload logs 
    for an explicit or implied timeframe.
    
    Returns a structured text payload containing critical mainframes performance indicators:
    - SQL Activity (SELECT, INSERT, UPDATE, DELETE statements executed)
    - Concurrency and Lock Suspensions (timeouts, deadlocks, claim waits)
    - Class 1 and Class 2 CPU Consumption (TCB time, zIIP time vs. elapsed time)
    - Transaction Volumes and commit/abort counts.
    - If Error is return , end it gracefully by explaining the error code.
    Requirements:
    - inp_date MUST follow the 'MM/DD/YYYY' format exactly.
    - inp_hour MUST be a two-digit string padded with a leading zero if necessary (e.g., '09' instead of '9').
    """
    # Call your original HTTP client function
    llm_ready_string = func_accounting_by_anyid(db2ssid=db2ssid,inpdate=inp_date,hr1=inp_hour)
    
    # Process it down into a clean, contextual summary string
    # llm_ready_string = process_db2_metrics_for_llm(raw_response)
    
    return llm_ready_string

tools=[tool_func_max_min_date,tool_accounting_by_hour_authid ,tool_accounting_by_authid,tool_accounting_by_anyid]

model_with_tools = model.bind_tools(tools=tools)


def llm_node(state : PRACagentState):
    # print(state)
    response = model_with_tools.invoke(state['messages'])
    # print(response)
    return {'messages' : response}

toolnode = ToolNode(tools)

def custom_router(state: PRACagentState):
    # print(state)
    # print("messages_state",state['messages'])
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # "error in custom"
        return "call_tools"
    return "end"

# def custom_router(state : PRACagentState):




PRACagent_flow = StateGraph(PRACagentState)




PRACagent_flow.add_node("llm_node",llm_node)
PRACagent_flow.add_node("toolnode",toolnode)

PRACagent_flow.add_edge(START,"llm_node")

PRACagent_flow.add_conditional_edges("llm_node",custom_router,
                                     {
                                         "call_tools" : "toolnode" ,
                                         "end" : END
                                     })

PRACagent_flow.add_edge("toolnode","llm_node")
# PRACagent_flow.add_edge("toolnode",END)


PRACagent = PRACagent_flow.compile(checkpointer = checkpointer)



