from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Literal
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode,InjectedState
from db2rep import func_max_min_date
from db2rep import func_accounting_by_hour_authid
from db2rep import func_accounting_by_authid
from db2rep import func_accounting_by_anyid
from db2repanyid import func_anyid_getaccreport
from langchain_core.messages import SystemMessage,HumanMessage,ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from datetime import datetime
from pydantic import BaseModel,Field
# from langchain_core.prompts import SystemMessagePromptTemplate


model = ChatOllama (model="gemma4:e4b",num_ctx=8192,temperature=0)

checkpointer = InMemorySaver()

class PRACagentState(TypedDict):
    messages : Annotated[list,add_messages]
    tool_response : Annotated[list,add_messages]
    tool_called : Annotated[list,add_messages]
    task_goal : list
    goal_achieved : bool
    itercount : int
    startdate :str
    enddate :str
    db2ssid : str

class TableStats(BaseModel):
    max_date: str =Field(description='maximum date recorded in table')
    min_date: str =Field(description='minimum date recorded in table')
    num_of_rows: int  =Field(description="number of rows in table")

@tool
def tool_func_max_min_date():
    '''
    this tool returns table data stats following is 
    oldest and latest timestamp recorded in the DMRACDTL table.
    number of rows in table.Use this for questions about row counts or dates.
    '''
    response = func_max_min_date()

    return TableStats( 
        max_date = response["max_date_in_table"],
        min_date = response["min_date_in_table"],
        num_of_rows= response['num_of_rows_in_table']
    )

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

# class ContextInfo(BaseModel):
#     db2ssid : str=Field(description="Db2 Subsystem Information")
#     inp_date : str=Field(description="Date for which report needs to be generated")
#     inp_hour : str=Field(description=" Hour for Each Day . " )

# @tool(args_schema=ContextInfo)
# def tool_accounting_by_anyid(db2ssid: str = "DMU1",
                                   
#                                    inp_date: str ="05/28/2026",
#                                    inp_hour:str = "00" ) -> str:
    
#     """
#     Queries the Db2 performance database to retrieve a consolidated accounting report 
#     for a specific subsystem, date, and hour interval.
    
#     Use this tool when the user asks for performance metrics, system health, or workload logs 
#     for an explicit or implied timeframe.
    
#     Returns a structured text payload containing critical mainframes performance indicators:
#     - SQL Activity (SELECT, INSERT, UPDATE, DELETE statements executed)
#     - Concurrency and Lock Suspensions (timeouts, deadlocks, claim waits)
#     - Class 1 and Class 2 CPU Consumption (TCB time, zIIP time vs. elapsed time)
#     - Transaction Volumes and commit/abort counts.
#     - If Error is return , end it gracefully by explaining the error code.
#     Requirements:
#     - inp_date MUST follow the 'MM/DD/YYYY' format exactly.
#     - inp_hour MUST be a two-digit string padded with a leading zero if necessary (e.g., '09' instead of '9').
#     """
#     # Call your original HTTP client function
#     llm_ready_string = func_accounting_by_anyid(db2ssid=db2ssid,inpdate=inp_date,hr1=inp_hour)
    
#     # Process it down into a clean, contextual summary string
#     # llm_ready_string = process_db2_metrics_for_llm(raw_response)
    
#     return llm_ready_string

class GetAccRep(BaseModel):
    db2ssid : str=Field(description="Db2 Subsystem Information")
    begdate : str=Field(description="Start Date")
    enddate : str=Field(description="End Date " )

@tool(args_schema=GetAccRep)
def tool_anyid_getaccreport(db2ssid: str , begdate : str ,enddate :str):

    '''
    get db2 account report for defined date period. 
    Input Parameters :
    begdate : start date
    enddate : end date

    Output will be markdown format will be returned.

    Requirements : 
    - dates MUST follow the 'MM/DD/YYYY' format exactly.
    - Begin Date will always be smaller than End Date
    - If only one Date is provided make begdate = enddate.

    '''
    
    llm_ready_string = func_anyid_getaccreport(db2ssid=db2ssid,begdate=begdate,enddate=enddate)
    
    # Process it down into a clean, contextual summary string
    # llm_ready_string = process_db2_metrics_for_llm(raw_response)
    
    return llm_ready_string

# tools=[tool_func_max_min_date,tool_accounting_by_hour_authid ,tool_accounting_by_authid,tool_accounting_by_anyid]
now = datetime.now()
formatted_date = now.strftime("%m/%d/%Y")       # e.g., 06/01/2026
day_of_week = now.strftime("%A")

tools=[tool_func_max_min_date,tool_accounting_by_hour_authid ,tool_accounting_by_authid,tool_anyid_getaccreport]

model_with_tools = model.bind_tools(tools=tools)

class SystemGoal(BaseModel):
    checklist: str = Field(description="A concrete bulleted list of criteria required to fulfill the user's request.")
    db2ssid : str = Field(description="Db2 Subsystem Id")
    startdate : str = Field(description="Star date of analysis ")
    enddate: str=Field(description="End date of analysis ")

def plannernode(state : PRACagentState):
    last_message = state['messages'][-1].content


    planner_prompt =f"""You are a Technical Planning Assistant for an expert Db2 Systems Programmer and Performance Reporter Agent. 

                    YOUR GOAL:
                    Break down user requests into a strict, objective, bulleted checklist that an expert Db2 DBA can use to verify a task is complete.

                    PLANNING RULES:
                    1. TECHNICAL PRECISION: Your checklist must include specific Db2 performance metrics (e.g., Getpages, Lock Suspends, Sync Read I/O, CPU time, Elapsed time).
                    2. DIAGNOSTIC MINDSET: 
                       If a real Db2 System Programmer will do this task , he will plan like this:
                            - identify which Db2 analysis needs to be performed and the dates for which analysis is needed.
                            - generate the accounting report for the db2 and dates . 
                            - From accouting report generated identify the top ids using high db2 resource based on get pages , high elapsed time and high cpu time
                            - Once Authid is identified drill further find the workload that was running for this authid in that hour.
                    3. SCOPE ENFORCEMENT: Ensure the plan requires the agent to identify specific timestamps or intervals before performing deep analysis.
                    4. FORMAT: Output your plan as a clear, numbered list of actionable technical requirements.
                    5. DATE RULES : 
                        - If query has day information as today , yesterday and last week or last 5 days , calculate actual dates relative to todays date.
                        - If query has day of week provided then calculate date of previous day and a day later . For eg : if query has Monday , calculate date for SUNDAY as start date and TUESDAY end date
                        - START DATE cannot be greater than END DATE
                        - date format always should be MM/DD/YYYY

                    To stay grounded today's Real world date is {formatted_date} {day_of_week}
                    """
    template = ChatPromptTemplate([
        ("system", planner_prompt),
        ("human", "{query}")
    ] )
    
    struct_llm = model.with_structured_output(SystemGoal)

    chain = template | struct_llm
    
    result = chain.invoke({"query": last_message})
    print("Output from Planner node")
    print(result)
    return { "task_goal" : result.checklist,
            "db2ssid" : result.db2ssid,
            "startdate" : result.startdate,
             "enddate" : result.enddate }



# class LLMStrucResponse(BaseModel):
def llm_node(state : PRACagentState): 
    
    messages = state['messages']
    
    # Check if we have a generated plan in the state
    task_goal = state.get('task_goal')
    db2ssid = state.get('db2ssid')
    
    if task_goal:
        # Inject the planner's hard rules and context right before the model decides
        context_prompt = (
            f"You are executing an automated Db2 performance analysis.\n"
            f"Target Subsystem: {db2ssid}\n"
            f"Analysis Timeframe: {state.get('startdate')} to {state.get('enddate')}\n"
            f"Your Execution Checklist:\n{task_goal}\n"
            f"Evaluate the current conversation history and tool outputs against this checklist. "
            f"If more data is required, continue calling tools sequentially."
        )
        # Prepend or append as a system message context
        messages = [SystemMessage(content=context_prompt)] + messages

    response = model_with_tools.invoke(messages)
    return {'messages': response}
    

toolnode = ToolNode(tools)

# def custom_router(state: PRACagentState):
#     # print(state)
#     # print("messages_state",state['messages'])
#     last_message = state["messages"][-1]
#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         # "error in custom"
#         return "call_tools"
#     return "end"

# def custom_router(state : PRACagentState):
class GoalAchieved(BaseModel):
    achieved: bool = Field(
        description="Whether the goal was achieved."
    )
def toolprocessnode(state: PRACagentState):
    last_message = state['messages'][-1]
    if isinstance(last_message,ToolMessage):
      return {'tool_response' : [last_message.content],
              'tool_called' : [last_message.name]}
    return

def goalverifynode(state: PRACagentState):
    # last_message = state['messages'][-1]
    tool_result = state["tool_response"]

    structured_llm = model.with_structured_output(GoalAchieved)

    result = structured_llm.invoke(
        f"""
        Determine if the user's goal has been achieved.

        Last tool response:
        {tool_result}

        Return achieved=true only if the tool output fully satisfies the goal.
        """
    )
    state['itercount'] = state['itercount'] + 1
    return {
        "goal_achieved": result.achieved,
        "itercount" :state['itercount']

    }
    

PRACagent_flow = StateGraph(PRACagentState)



PRACagent_flow.add_node("plannernode",plannernode)

PRACagent_flow.add_node("llm_node",llm_node)
PRACagent_flow.add_node("toolnode",toolnode)
PRACagent_flow.add_node("toolprocessnode",toolprocessnode)
PRACagent_flow.add_node("goalverifynode",goalverifynode)

PRACagent_flow.add_edge(START,"plannernode")
PRACagent_flow.add_edge("plannernode","llm_node")

PRACagent_flow.add_conditional_edges("llm_node",tools_condition,
                                     {
                                         "tools" : "toolnode" ,
                                         "__end__" : END
                                     })

PRACagent_flow.add_edge("toolnode","toolprocessnode")
PRACagent_flow.add_edge("toolprocessnode","goalverifynode")

def custrouter(state : PRACagentState):
    if state["goal_achieved"] or state['itercount'] == 3 :
        return "END"
    else:
        return "llm_node"
    
PRACagent_flow.add_conditional_edges("goalverifynode",custrouter,
                                     {
                                       "llm_node" :"llm_node",
                                       "END" : END
                                       })

# PRACagent_flow.add_edge("toolnode",END)


PRACagent = PRACagent_flow.compile(checkpointer = checkpointer)

# print(PRACagent.get_graph().draw_mermaid())



