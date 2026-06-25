from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage
import apicall
from typing import TypedDict,Annotated
# from pydantic import BaseModel
import operator
import zparmsp
import lstdb2
# from lstdb2 import get_data_view
from langgraph.checkpoint.memory import InMemorySaver

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState


model = ChatOllama(model="gemma4:e4b" ,
                    temperature=0,num_ctx=8192)

# Initialize Embeddings (must match the processor)
embeddings = OllamaEmbeddings(model="embeddinggemma:300m")
# r=model.invoke("What is Capital of India ?").content
vectorstore = FAISS.load_local(
    "faiss_db2zparm_index", 
    embeddings, 
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_type='similarity',search_kwargs={"k": 3})

class TState(TypedDict):
    messages: Annotated[list, operator.add]



# @tool
# def getzparmvaluetool(zparm : str , context :str ):
#     ''' this tool returns the value of a zparm .
#     function takes zparm as input 
#     zparm is parameter name db2 configuration value 
#     context is the target db2 name monitored by the backend api 
#     zparms are also called subsystem parameters 
#     Args:
#         zparm: The parameter name (e.g., 'TCPALVER').
#         context: The unique 'target_context' string retrieved from the monitoring list.
#                  CRITICAL: Do NOT use the db2_ssid. Use the 'target_context' value 
#                  (e.g., use 'DMU1DB2A', not 'DMU1').
#     '''
    
#     return zparmsp.getzparm_value(zparm,context)

@tool
def getzparm_alltool(context :str ):
    ''' this tool returns dictionary of all zparm values for the context .
    return value contains zparmname and tuple containing its value and macroname where zparm lives.
    function takes context as input 
    context is the target db2 name monitored by the backend api 
    zparms are also called subsystem parameters '''
    return zparmsp.getzparm_all(context)

# @tool
# def comparezparm_tool(ssid1 :str , ssid2 :str ):
#     ''' this tool compare zparms of db2 ssid1 with ssid2
#     returns dictionary of 2 keys 
#     1 : non matching zparms and their settings
#     2 : non existing zparms , existing in ssid1 but not in ssid 2
    
#     function takes 2 parameter as input which are db2 ssid.
#     context is the target db2 name monitored by the backend api 
#     zparms are also called subsystem parameters '''
#     return zparmsp.zparm_compare([ssid1,ssid2])

@tool
def list_monitored_Db2tool(context :str , state: Annotated[dict, InjectedState]):
    ''' Function :Purpose to show all the Db2 that are being monitored 
        Accepts context as input which is CURRSYS .
        Returns a dictionary where key is target db2 monitored and value is db2 subsystem id.
    '''
    print(state.get("messages",[]))
    return lstdb2.list_monitored_Db2(context)

# @tool
# def db2_rag_tool(query: str):
#     '''
#     use this tool to refer pdf documentation related to Db2 zparms.
#     document it refers is for Db2 v13. Use it to explain user questions related to
#     zparm explainations and value limits and impacts. While replying put your perpective from datasharing db2 also
#     When user specifies text instead of actual zparm name check in documentation for actual value of zparm . 
#     For eg. tcp already verified is text is TCPALVER is actual zparm name.

#     '''
#     resultrag = retriever.invoke(query)
#     content =[doc.page_content for doc in resultrag]
#     metadata =[doc.metadata for doc in resultrag]
#     return {
#         'query' : query,
#         'content' : content,
#         'metadata' : metadata
#     }

#access to only two tools
tools=[getzparm_alltool,list_monitored_Db2tool ]

model_with_tools = model.bind_tools(tools)

graph = StateGraph(TState)

checkpoint = InMemorySaver()

def decisionmaker(state : TState) :
    response = model_with_tools.invoke(state['messages'])
    return {"messages" : [response]}

toolnode = ToolNode(tools)


graph.add_node("decisionmaker",decisionmaker)
graph.add_node("tool_node",toolnode)
graph.add_edge(START,"decisionmaker")
graph.add_conditional_edges("decisionmaker",tools_condition,
                            {"tools": "tool_node",  # Match your node name exactly
        END: END})
graph.add_edge("tool_node","decisionmaker")
servicenode = graph.compile(checkpointer=checkpoint)

config = {"configurable": {"thread_id": "db2_session_001"}}
while True: 
    print("Chat Begins:")
    user_input = input("User:")
    if user_input.lower() in ["bye","quit","exit"]:
        break
    if len(user_input) == 0 :
        # print(len(user_input))
        continue
    sys_msg = SystemMessage(content=(
    "You are a Db2 Expert and seasoned Db2 System Programmer for z/OS. "
    "Your goal is to assist users with technical queries, diagnostics, and configuration values. "
    
    "\nFollow these guidelines:\n"
    
    "1. Always refer to the product as 'Db2' (never 'DB2').\n"
    "2. Before answering, determine if you need to call a tool. If a user asks for a 'zparm' or 'subsystem parameter' "
    "but doesn't provide a context (SSID), inkoke tool to find out which are monitored Db2.\n"
    "3. If a question is ambiguous or lacks necessary details to call a tool, politely ask the user for clarification.\n"
    "4. Base your technical answers on the data returned by the tools. If the tools return an error, "
    "report the error clearly rather than guessing.\n"
    "5. Never take any actions such as issue commands always ask user for his approval .\n"
    "6. If a tool returns a large list of data, do not repeat the whole list. Instead, summarize the findings or acknowledge that the data has been loaded and ask the user for specific parameters they are interested in.\n"
    "7. Target Context and Db2 name are different . API Uses Target Name for api call not db2 ssid . Target context is Db2 regions that are in scope of monitoring and it is excusive to APIs.\n"
    "8. When using db2_rag_tool , ONLY answer based on the provided text. If the retrieved text does not explicitly mention a specific detail  state: 'The documentation provided does not specify the rules for [Topic].'DO NOT infer, assume, or use general knowledge to fill in gaps." 
    "9. Always validate for actual zparm name by checking in db2_rag_tool"        
        ))
    
    init_state = {"messages": [sys_msg,HumanMessage(content=f"{user_input}")]}
    # print(servicenode.get_state_history(config=config))
    result = servicenode.invoke(init_state,config=config)
    # for chunk in servicenode.stream(init_state,config=config):
    #     for node_name, state_update in chunk.items():
    #         print(f"\n--- Node: {node_name} ---")
    #         # This shows you the messages added by each node
    #         if "messages" in state_update:
    #             last_msg = state_update["messages"][-1]
    #             print(f"Content: {last_msg.content}")
    #             if hasattr(last_msg, 'tool_calls'):
    #                 print(f"Tool Calls: {last_msg.tool_calls}")

    # print(result)
    print("AI: ",result['messages'][-1].content)
    print("Token used in this conversation: ",result['messages'][-1].usage_metadata)

