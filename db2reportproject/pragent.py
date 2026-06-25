from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from db2rep import func_max_min_date
from db2rep import func_accounting_by_hour_authid
from db2rep import func_accounting_by_authid
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
    llm_ready_string = func_accounting_by_authid(db2ssid=db2ssid,inpdate=inp_date,hr1=inp_hour)
    
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

config = {"configurable": {"thread_id": "db2_session_001"}}


now = datetime.now()
formatted_date = now.strftime("%m/%d/%Y")       # e.g., 06/01/2026
day_of_week = now.strftime("%A")

print("Todays date is:  ",formatted_date )
print("Day of Week is:  ",day_of_week )
# system_prompt = SystemMessage(content= """You are Db2 Accounting Reporter Agent .\n
#                               Obey the following rules \n.
#                               1. Always refer Db2 as Db2 not DB2.
#                               2. You will have access to Db2 accounting report which is by hour interval.
#                               3. The current real-world date is {current_date} ({day_of_week}).
#                               4. If the user does not provide or ask generically generate dates automatic by yourself in MM/DD/YYYY format.
#                               For eg. generate accounting report for today . so today will be 05/29/2026 .
                                                            
#                               """)


system_prompt_content = """You are an expert Db2 Systems Programmer and Performance Reporter Agent. 

REASONING PROTOCOL:
- Before executing a tool call or delivering a final response, you MUST output a brief, logical "Chain of Thought" reasoning step.
- Wrap this internal analysis inside `<thinking>` and `</thinking>` XML tags.
- In this section, clearly state:
  1. What the user is asking.
  2. What metrics or dates you need to investigate.
  3. Which tool or action makes the most sense to use next.

ROLE & BEHAVIOR:
- Your core objective is to analyze hourly Db2 accounting reports to identify performance trends, bottlenecks, and anomalies.
- Act like an experienced mainframe DBA: do not just repeat numbers; highlight systemic issues (e.g., locking, high I/O, or heavy CPU consumption).

STRICT OPERATIONAL RULES:
1. NOMENCLATURE: Always use exact capitalization for "Db2". Never write it as "DB2".
2. DATA SOURCE: You have access to specialized tool utilities providing hourly interval data metrics (e.g., Getpages, Lock Suspends, Sync Read I/O).
3. TEMPORAL ANCHOR (CRITICAL): If the user requests data for generic timeframes (like "today" or "yesterday") without specifying an exact date string, calculate the target dates relative to today's date: **05/29/2026** (Format: MM/DD/YYYY).
4. The current real-world date is {current_date} ({day_of_week}).
5. If a query yields no data or an answer cannot be provided, do not give a generic failure response. Provide a clear, technical justification explaining why the data is unavailable (e.g., the requested hour interval falls outside the report boundary, no active threads were recorded during that window, or the required SMF counter fields are missing).
6. Absolute Timeframe Enforcement: You must never guess, assume, or default to an hour interval if the user's prompt is missing a specific timeframe. You must first invoke your interval discovery tools to locate active processing windows.

DIAGNOSTIC GUIDELINES FOR HOURLY METRICS:
- High Elap Time + Low CPU Time = External delays (Lock/Latch suspensions, Enqueues, or z/OS Storage Subsystem queuing).
- High Elap Time + High CPU Time = Heavy application processing, unindexed queries, or massive Getpage loops.
- Correlate spikes in 'MAX_PGLOCKS' or 'AVG_LOCK_SUSPENDS' with application response degradation.
"""
system_prompt_content = system_prompt_content.format(current_date = formatted_date , day_of_week=day_of_week)
system_prompt = SystemMessage(content=system_prompt_content.strip())

# user_prompt = HumanMessage(content= " for 28th may 2026 can you generate Db2 accounting report for authid BMCADM for Db2 DNK3 ? Analyse the report and let me know where I need to pay attention" )
print("PR Agent is initialized ......\n")
print("You can ask questions now. \n")
while True :
    
    user_input = input("You >")
    if user_input.lower() in ['bye','quit','exit'] :
        break
    if len(user_input) == 0:
        continue

    # user_prompt = HumanMessage(content= " Tell me during which hour of day MVSMKJ was highly active and which specific thread from mvsmkj used maximum resource on DMU1 Db2 ? " )
    user_prompt = HumanMessage(content=user_input)
    init_prompt = {"messages" : [system_prompt,user_prompt]}

    # result =  PRACagent.invoke(init_prompt,config=config)

    # print(result['messages'][-1].content)
    # print(result['messages'][-1].usage_metadata)
# # print("Usage Metadata : " ,result.usage_metatdata)
# for chunk in PRACagent.stream(init_prompt,config=config):
        
#         # print(chunk.items())
#         for node_name, state_update in chunk.items():

#             print(f"\n--- Node: {node_name} ---")
#             # This shows you the messages added by each node
#             if "messages" in state_update:

#                 last_msg = state_update["messages"][-1]

#                 print(f"Content: {last_msg.content}")
#                 if hasattr(last_msg, 'tool_calls'):
#                     print(f"Tool Calls: {last_msg.tool_calls}")
#                 if hasattr(last_msg, 'usage_metadata'):
# #                     print(f"Token Usage: {last_msg.usage_metadata}")
#     for chunk in PRACagent.stream(init_prompt,config=config):
#         for nodename,statupdate in chunk.items():
#             print(f"*****************{nodename}**************")
#             print(statupdate)

    for chunk in PRACagent.stream(init_prompt, config=config, stream_mode="updates"):
        for node_name, state_update in chunk.items():
            print(f"\n==================== NODE: {node_name} ====================")
            
            if "messages" in state_update:
                # state_update["messages"] can be a list or a single Message object depending on the node
                messages = state_update["messages"]
                if not isinstance(messages, list):
                    messages = [messages]
                
                for msg in messages:
                    # 1. Print Chain of Thought / Thinking if present
                    if msg.content:
                        print(f"[{msg.__class__.__name__} Content]:\n{msg.content}")
                    
                    # 2. Print Tool Calls if the LLM decided to invoke a tool
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        print(f"\n--- Tool Calls Formulated by LLM ---")
                        for tc in msg.tool_calls:
                            print(f" Tool Name : {tc['name']}")
                            print(f" Arguments : {tc['args']}")
                            print(f" Call ID   : {tc['id']}")
                    
                    # 3. Print Token Usage Data if available
                    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        print(f"\n[Token Usage]: {msg.usage_metadata}")
                        
    print("\n==================== EXECUTION COMPLETE ====================\n")

