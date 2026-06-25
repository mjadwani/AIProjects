
from langchain_core.messages import AIMessage,HumanMessage,ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

# from langgraph.prebuilt
# state = {'messages': AIMessage(content='', additional_kwargs={}, 
#          response_metadata={'model': 'gemma4:e4b', 'created_at': '2026-05-29T09:45:39.8576454Z', 
#                             'done': True, 'done_reason': 'stop', 'total_duration': 50379690200, 'load_duration': 419040700, 
#                             'prompt_eval_count': 95, 'prompt_eval_duration': 101951600, 'eval_count': 618, 'eval_duration': 49595565700, 
#                             'logprobs': None, 'model_name': 'gemma4:e4b', 'model_provider': 'ollama'}, id='lc_run--019e731f-4441-7a43-9086-429697f6dfde-0', 
#                             tool_calls=[{'name': 'tool_func_max_min_date', 'args': {}, 'id': '2537bfa2-8d77-46c2-ac44-348fa9bbaa33', 'type': 'tool_call'}], 
#                             invalid_tool_calls=[], usage_metadata={'input_tokens': 95, 'output_tokens': 618, 'total_tokens': 713})}


# # print(state['messages'].tool_calls)



# if (hasattr(state['messages'],'tool_calls') ) :
#     print(state['messages'].tool_calls)


# result = {'messages': [HumanMessage(content=' How many rows are there in PRACTDTL Table ?', additional_kwargs={}, response_metadata={}, id='ee9d2ed1-fbc6-4058-a4df-289c42c82e98'), 
#                        AIMessage(content='', additional_kwargs={}, response_metadata={'model': 'gemma4:e4b', 'created_at': '2026-05-29T10:25:16.2150538Z', 'done': True, 'done_reason': 
#                                                                                       'stop', 'total_duration': 44438898900, 'load_duration': 511860700, 'prompt_eval_count': 95, 'prompt_eval_duration': 84605900, 'eval_count': 583, 
#                                                                                       'eval_duration': 43610508100, 'logprobs': None, 'model_name': 'gemma4:e4b', 'model_provider': 'ollama'}, id='lc_run--019e7343-9e1d-7a72-aad8-0d0fa4e4d4e6-0', 
#                                                                                       tool_calls=[{'name': 'tool_func_max_min_date', 'args': {}, 'id': '444b743c-6db2-43b9-82bf-e6d41bc71235', 'type': 'tool_call'}], 
#                                                                                       invalid_tool_calls=[], usage_metadata={'input_tokens': 95, 'output_tokens': 583, 'total_tokens': 678}), 
#                                                                                       ToolMessage(content='{"response": {"max_date_in_table": "2026-05-29-02.37.58.370847", "min_date_in_table": "2025-02-13-01.42.59.241515", ' \
#                                                                                       '"num_of_rows_in_table": 16810112}}', name='tool_func_max_min_date', id='0d916425-e3df-4b4f-a5cf-b67758b83b19', 
#                                                                                       tool_call_id='444b743c-6db2-43b9-82bf-e6d41bc71235'), 
#                                                                                       AIMessage(content='There are 16,810,112 rows in the PRACTDTL Table.', additional_kwargs={}, 
#                                                                                                 response_metadata={'model': 'gemma4:e4b', 'created_at': '2026-05-29T10:25:44.9835054Z', 'done': True, 'done_reason': 'stop', 
#                                                                                                                    'total_duration': 19384914500, 'load_duration': 512950700, 'prompt_eval_count': 218, 'prompt_eval_duration': 2385738900, 
#                                                                                                                    'eval_count': 214, 'eval_duration': 16360866700, 'logprobs': None, 'model_name': 'gemma4:e4b', 'model_provider': 'ollama'}, 
#                                                                                                                    id='lc_run--019e7344-705b-7751-a0a2-035ae0ed963b-0', tool_calls=[], invalid_tool_calls=[], 
#                                                                                                                    usage_metadata={'input_tokens': 218, 'output_tokens': 214, 'total_tokens': 432})]}


# print(result['messages'],"\n")
# print(type(result['messages']))
# print(result['messages'][-2])
# print(type(result['messages'][-2]))
# last_message = result['messages'][-2]
# if hasattr(last_message,"tool_calls") and last_message.tool_calls :
#     print(True)
# else:
#     print(False)

# last_message = result['messages'][-2]
# print("checkInstance")
# if isinstance(last_message,ToolMessage):
#       print(True)
#       print(last_message.content)
#       print(last_message.name)
# else:
#     print(False)


# # text= 112

# # var = """

# # hello I am manoj . My number is {text}

# # """

# # varnew= var.format(text=123)

# # print(varnew ) 

# chunk = {'llm_node': {'messages': AIMessage(content='<thinking>\n1. **User Request:** The user wants to know the total number of rows and the minimum and maximum dates recorded in the accounting table.\n2. **Metrics/Dates Needed:** Row count, Min Date, Max Date.\n3. **Tool Selection:** The `tool_func_max_min_date` tool is designed to provide exactly these statistics (row count, oldest timestamp, latest timestamp).\n</thinking>\n', additional_kwargs={}, response_metadata={'model': 'gemma4:e4b', 'created_at': '2026-06-04T18:59:32.8707877Z', 'done': True, 'done_reason': 'stop', 'total_duration': 23115095300, 'load_duration': 562587200, 'prompt_eval_count': 686, 'prompt_eval_duration': 117322300, 'eval_count': 255, 'eval_duration': 22261131700, 'logprobs': None, 'model_name': 'gemma4:e4b', 'model_provider': 'ollama'}, id='lc_run--019e9400-ef39-7df0-b52e-7966fefab555-0', tool_calls=[{'name': 'tool_func_max_min_date', 'args': {}, 'id': '8673f72c-2c25-4ca5-8d0b-188a60b9302e', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 686, 'output_tokens': 255, 'total_tokens': 941})}}

# for node,statusupdate in chunk.items():
#      print("node name",node)
#      print("update",statusupdate['messages'].content)
     

# typetest = ToolMessage(content="max_date='2026-06-04-14.29.53.264889' min_date='2025-02-13-01.42.59.241515' num_of_rows=17790232", name='tool_func_max_min_date', id='5cabd8e4-d34e-4fe2-9ae3-3cf807585764', tool_call_id='5d27706b-1460-4d1b-9691-a85f2417965a')

# print(type(typetest)==list)
# now = datetime.now()
# formatted_date = now.strftime("%m/%d/%Y")       # e.g., 06/01/2026
# day_of_week = now.strftime("%A")

# planner_prompt =f"""You are a Technical Planning Assistant for an expert Db2 Systems Programmer and Performance Reporter Agent. 

#                     YOUR GOAL:
#                     Break down user requests into a strict, objective, bulleted checklist that an expert Db2 DBA can use to verify a task is complete.

#                     PLANNING RULES:
#                     1. TECHNICAL PRECISION: Your checklist must include specific Db2 performance metrics (e.g., Getpages, Lock Suspends, Sync Read I/O, CPU time, Elapsed time).
#                     2. DIAGNOSTIC MINDSET: If the user asks to "check performance," your plan must include steps to correlate high elapsed time with either high CPU (application issues) or low CPU (external delays/locking).
#                     3. SCOPE ENFORCEMENT: Ensure the plan requires the agent to identify specific timestamps or intervals before performing deep analysis.
#                     4. FORMAT: Output your plan as a clear, numbered list of actionable technical requirements.
#                     5. DATE FORMATING : 
#                         - If the query only has a single date then broaden the period of analysis . For eg. if data provided is 3 June . Do analysis from 2 June as start date and 4th June as end date.
#                         - If query has day information as today , yesterday and last week or last 5 days , calculate actual dates relative to todays date.
#                         - If query has day of week provided then calculate date of previous day and a day later . For eg : if query has Monday , calculate date for SUNDAY as start date and TUESDAY end date

#                     Example of your planning style:
#                     - Identify the specific hour interval for the reported issue.
#                     - Identify for which Db2 the analysis needs to be done.
#                     - Extract dates and Time interval from the user query .
#                     - If your ask for generic question you must plan for series of steps that will be needed to achieve the goal
                    
#                     Today's Real world date is {formatted_date} {day_of_week}
#                     """
# template = ChatPromptTemplate([
#         ("system", planner_prompt),
#         ("human", "{query}")
#     ] )

# print(template)

checklist='''## Db2 Performance Analysis Checklist for DMU1 (02/06/2026 - 04/06/2026)' db2ssid='DMU1' startdate='02/06/2026' enddate='04/06/2026'
content='<thinking>\n1. **User Request:** The user is reporting a Db2 slowdown for the SSID `DMU1` on June 3rd, 2026, and wants the root cause identified.\n2. **Metrics/Dates Needed:** The primary date is 06/03/2026. I need general activity metrics for this entire day to identify resource spikes (CPU, I/O, Locks).\n3. **Tool Selection:** The `tool_anyid_getaccreport` is the most appropriate initial tool as it allows me to pull a comprehensive report for the entire specified date range (`begdate` and `enddate`) for the given SSID, without needing a specific `authid` or hourly breakdown yet.\n</thinking>\n' additional_kwargs={} response_metadata={'model': 'gemma4:e4b', 'created_at': '2026-06-05T11:29:48.0570946Z', 'done': True, 'done_reason': 'stop', 'total_duration': 92451549400, 'load_duration': 525071700, 'prompt_eval_count': 1134, 'prompt_eval_duration': 27500650300, 'eval_count': 688, 'eval_duration': 63415866300, 'logprobs': None, 'model_name': 'gemma4:e4b', 'model_provider': 'ollama'} id='lc_run--019e978a-7af2-7262-bf78-a34d7336d431' tool_calls=[{'name': 'tool_anyid_getaccreport', 'args': {'begdate': '06/03/2026', 'db2ssid': 'DMU1', 'enddate': '06/03/2026'}, 'id': 'c8d0d63c-7cf8-4f16-be07-96fefbac8af1', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 1134, 'output_tokens': 688, 'total_tokens': 1822}'''