import streamlit as st
from datetime import datetime
from langchain.messages import HumanMessage,SystemMessage
# from backend import PRACagent
# from newbackend import PRACagent
from backendsimple import PRACagent
import time

CONFIG = {"configurable": {"thread_id": "db2_session_001"}}

# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")

st.title("Performance Reporter Agent")

if len(st.session_state)==0 :
    st.session_state['message'] =[]
    # st.session_state['token_history'] =[]

# print('after',bool(st.session_state))
# print(st.session_state)
if st.session_state['message']:
    for each in st.session_state['message']:
        # print(each)
        for k,v in each.items():
            if k == 'ai':
                with st.chat_message(k):
                    st.write(v[0])
                    with st.expander("Token Usage"):
                        st.write(v[1])
            else:
                with st.chat_message(k):
                    st.write(v)


user_input = st.chat_input("Ask your question ?")

# if user_input:
#     st.text(user_input)










now = datetime.now()
formatted_date = now.strftime("%m/%d/%Y")       # e.g., 06/01/2026
day_of_week = now.strftime("%A")

# print("Todays date is:  ",formatted_date )
# print("Day of Week is:  ",day_of_week )
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
7. Output Length: "Keep responses under 30 words when providing data stats."

DIAGNOSTIC GUIDELINES FOR HOURLY METRICS:
- High Elap Time + Low CPU Time = External delays (Lock/Latch suspensions, Enqueues, or z/OS Storage Subsystem queuing).
- High Elap Time + High CPU Time = Heavy application processing, unindexed queries, or massive Getpage loops.
- Correlate spikes in 'MAX_PGLOCKS' or 'AVG_LOCK_SUSPENDS' with application response degradation.


"""
system_prompt_content = system_prompt_content.format(current_date = formatted_date , day_of_week=day_of_week)
system_prompt = SystemMessage(content=system_prompt_content.strip())

# user_prompt = HumanMessage(content= " for 28th may 2026 can you generate Db2 accounting report for authid BMCADM for Db2 DNK3 ? Analyse the report and let me know where I need to pay attention" )
# print("PR Agent is initialized ......\n")
# print("You can ask questions now. \n")
# while True :
    
#     user_input = input("You >")
#     if user_input.lower() in ['bye','quit','exit'] :
#         break
#     if len(user_input) == 0:
#         continue

    # user_prompt = HumanMessage(content= " Tell me during which hour of day MVSMKJ was highly active and which specific thread from mvsmkj used maximum resource on DMU1 Db2 ? " )


print("hello")
if user_input:
    st.session_state['message'].append({'user' : user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    
    # print(result)
    # last_message = result['messages'][-1].content
    user_prompt = HumanMessage(content=user_input)
    init_prompt = {"messages" : [system_prompt,user_prompt],
                   "tool_response":[],
                   "tool_called": [],
                   "task_goal":[],
                   "goal_achieved":False,
                   "itercount":0,
                   "startdate":"",
                   "enddate":""}

    with st.chat_message('ai'):
        
        # st.text(last_message)
        # last_message= st.write_stream(
        #     chunk.content for chunk,metadata in PRACagent.stream(init_prompt,
        #                       config=CONFIG,
        #                       stream_mode='messages'))
        token_usage=[]
        def stream_wrapper() :
            chunks = PRACagent.stream(init_prompt,
                                config=CONFIG,
                                stream_mode='messages')
            for chunk, metadata in chunks:
                if chunk.content:
                    yield chunk.content
            
                if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                    token_usage.append(f"-----NodeName-------{metadata["langgraph_node"]}")
                    token_usage.append(chunk.usage_metadata)
                    
                    
                
            
        last_message=st.write_stream(stream_wrapper())
        
        st.session_state['message'].append({'ai' : [last_message,token_usage]})

                
        with st.expander("Token Usage"):
            st.write(token_usage)

