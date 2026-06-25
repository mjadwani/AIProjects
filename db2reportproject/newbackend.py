from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
import json
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage,HumanMessage
import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from db2rep import func_accounting_by_anyid,func_accounting_by_authid,func_accounting_by_hour_authid,func_max_min_date
from pydantic import BaseModel,Field

class PRACagentState(TypedDict):
    messages: Annotated[list, add_messages]
    # Track diagnostic state across node iterations
    target_ssid: Optional[str]
    target_date: Optional[str]
    target_hour: Optional[str]
    suspect_authids: List[str]      # Mainframe IDs identified as heavy resource users
    root_cause_found: bool          # Flag to let the graph know when to wrap up


model = ChatOllama (model="granite4.1:8b",num_ctx=8192,temperature=0)
checkpointer = InMemorySaver()


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
# --- 1. System Prompt with Temporal/Operational Context ---
# Providing the exact current date enables the agent to compute relative lookups ("today", "yesterday")
# CURRENT_SYSTEM_CONTEXT = f"Current Date: {datetime.now().strftime('%m/%d/%y')}. Subsystem Default: DMU1."
# {CURRENT_SYSTEM_CONTEXT}


SYSTEM_PROMPT = f"""You are an expert Db2 for z/OS System Programmer Agent.

Your goal is to autonomously diagnose performance anomalies using available tools.
When given an incident or symptom:
1. Identify the target subsystem, date, and hour.
2. Query general metrics for that time window.
3. Inspect the results for bottlenecks (e.g., high Class 2 CPU, lock suspensions, high statement executions).
4. Extract offending AuthIDs and drill down into individual thread metrics automatically.
5. Provide a clear summary explaining the root cause and any relevant Db2 SQL codes.
"""

# --- 2. Upgraded Node Definitions ---

def llm_node(state: PRACagentState):
    """Primary routing and thinking node."""
    messages = state['messages']
    
    # Inject system instruction if it's the start of the conversation
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = model_with_tools.invoke(messages)
    return {'messages': response}

def triage_node(state: PRACagentState):
    """
    Autonomous evaluation node.
    Inspects the last tool message to extract operational findings 
    and determines if further drill-down tool invocations are needed.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Ensure we are evaluating a tool response
    if last_message.type != "tool":
        return state

    tool_output = last_message.content
    
    # Prompt the LLM to inspect the tool payload specifically for anomalies
    triage_prompt = f"""
    Analyze this raw Db2 metrics payload and determine if specific authorization IDs (authid)
    are causing resource constraints (e.g., high CPU, high suspensions).
    Return your analysis as JSON matching this structure:
    {{
        "suspect_authids": ["LIST", "OF", "IDS"],
        "anomaly_detected": true/false,
        "reason": "Brief summary of problem"
    }}
    
    Payload:
    {tool_output}
    """
    
    # Utilize structured output capabilities if supported, or parse raw JSON string
    triage_response = model.invoke([HumanMessage(content=triage_prompt)])
    
    try:
        data = json.loads(triage_response.content)
        new_suspects = data.get("suspect_authids", [])
        # Append found suspects to our State history tracking
        updated_suspects = list(set(state.get("suspect_authids", []) + new_suspects))
        
        return {
            "suspect_authids": updated_suspects,
            "root_cause_found": not data.get("anomaly_detected", False) or len(updated_suspects) == 0
        }
    except Exception:
        # Fallback if local model parsing fails
        return state

# --- 4. Advanced Routing Logic ---

def autonomous_router(state: PRACagentState) -> Literal["call_tools", "evaluate_triage", "end"]:
    """Determines the next optimal leg of the diagnostic journey."""
    last_message = state["messages"][-1]
    
    # If the LLM requested a tool execution, route directly to ToolNode
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
        
    # If a tool just completed, send it to the triage evaluation node
    if last_message.type == "tool":
        return "evaluate_triage"
        
    # If the triage node signals completion or LLM naturally terminates, end the execution
    if state.get("root_cause_found") == True:
        return "end"
        
    return "end"

# --- 5. Building the Autonomous Graph Workflow ---

workflow = StateGraph(PRACagentState)

# Add standard and analytical nodes
workflow.add_node("llm_node", llm_node)
workflow.add_node("toolnode", ToolNode(tools))
workflow.add_node("triage_node", triage_node)

# Core Execution Flow
workflow.add_edge(START, "llm_node")

# Routing after LLM interactions
workflow.add_conditional_edges(
    "llm_node",
    autonomous_router,
    {
        "call_tools": "toolnode",
        "end": END
    }
)

# Routing after Tool execution to pass through the Triage Evaluator
workflow.add_edge("toolnode", "triage_node")

# Routing after Triage evaluation back into the LLM to process next logical steps
workflow.add_conditional_edges(
    "triage_node",
    lambda state: "llm_node" if not state.get("root_cause_found") else "end",
    {
        "llm_node": "llm_node",
        "end": END
    }
)

PRACagent = workflow.compile(checkpointer=checkpointer)