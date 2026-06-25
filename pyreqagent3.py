from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START,END,StateGraph
from langgraph.graph.message import add_messages
from typing import TypedDict,Annotated
from pydantic import BaseModel,Field
from langchain.tools import tool, ToolRuntime,InjectedState
# from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.messages import SystemMessage,HumanMessage
import operator
from langgraph.checkpoint.memory import InMemorySaver
import json
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor

# Wrap your existing retriever block


model = ChatOllama(model="gemma4:e4b",num_ctx=8192)

def retriever_block(top_k_val : int ) :
    embedding_model = OllamaEmbeddings(model="embeddinggemma:latest")
    vectorstore = FAISS.load_local(
        folder_path="C:\\Users\\mjadwani\\Documents\\langgraphpractice\\faiss_db2zparm_index",
        index_name="index",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True

                     )

    # retriever = vectorstore.as_retriever(search_type =  "similarity" ,search_kwargs={"k":top_k_val})

    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    compressor = LLMChainExtractor.from_llm(model)

# This retriever automatically compresses text on the fly!
    compressed_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, 
    base_retriever=base_retriever
    )
    return compressed_retriever

@tool
def rag_tool(query :str , state: Annotated[dict, InjectedState] ) -> dict :
    """
    Tool purpose is to provide response to input query 
    by referencing the local rag knowledge which requirement.txt file .
    query is input parameter and is not optional
    """
    # k_val=runtime.state["top_k"]
    print("Agent State",state)
    k_val = state.get("top_k",2)

    # query = state["query"]
    retriever=retriever_block(k_val)
    result_rag = retriever.invoke(query)
    content = [doc.page_content for doc in result_rag]
    return {
        "query" : query ,
        "content" : content
    }

tools= [rag_tool]

model_with_tools= model.bind_tools(tools)

class RAGAgentState(TypedDict):
    query : Annotated[list,add_messages]
    top_k : int
    loop_count: int             # Circuit breaker to prevent infinite loops
    eval_is_complete: bool      # Stores evaluator verdict

class EvalStruct(BaseModel):
    is_complete : bool = Field(description="doc reference is complete")
    reason : str =Field(description="explain why is_complete true of false")

model_with_structresponse= model.with_structured_output(EvalStruct)

def llm_node(state: RAGAgentState):
    response = model_with_tools.invoke(state["query"])
    return {"query" : [response]}

##########################
#evaluator node
##########################


def evaluator_node(state: RAGAgentState):
    print("\n--- Node: evaluator_node ---")
    print('agent state',state)
    # Extract the tool output from the message history to inspect raw text chunks
    last_msg = state["query"][-1]
    
    retrieved_context = last_msg.content  # This contains the JSON string returned by ToolNode
    
    eval_prompt = (
        "You are an expert DB2 systems inspector auditing documentation completeness.\n"
        "Review the raw retrieved text chunks provided below. Look carefully for truncated information, "
        "missing parameters, or statements like 'continued on page...' or lists that cut off.\n"
        "Determine if the current context contains ENOUGH comprehensive information to answer completely.\n\n"
        "You MUST respond exclusively in JSON format with this exact structure:\n"
        "{\n"
        "  \"is_complete\": true or false,\n"
        "  \"reason\": \"Brief explanation of your judgment\"\n"
        "}\n\n"
        f"RETRIEVED TEXT CHUNKS:\n{retrieved_context}"
    )
    
    # Run a dedicated, cold call (temp 0.0) to check documentation completeness
    response = model_with_structresponse.invoke(
        [HumanMessage(content=eval_prompt)],
        options={"temperature": 0.0, "format": "json"}
    )
    print("structured_reponse\n",response)
    # try:
    #     eval_data = json.loads(response.content)
    #     print(f"[EVALUATION VERDICT]: {eval_data}")
    #     is_complete = eval_data.get("is_complete", True)
    # except Exception:
    #     print("[EVALUATION ERROR] Failed to parse JSON. Defaulting to true to prevent loops.")
    #     is_complete = True
        
    return {
        "eval_is_complete": response.is_complete,
        "loop_count": state["loop_count"] + 1
    }

# # New action node that updates graph parameters when router requests expansion
# def expand_search_node(state: RAGAgentState):
#     # Dynamically upscale top_k by 3 elements and reset verification flag to avoid sticky routing states
#     new_k = state["top_k"] + 3
    
#     # Reconstruct a cleaner message history or let it overwrite via system instructions
#     # We strip the failed evaluation and tool call to force the LLM to reissue a wider lookup
#     return {
#         "top_k": new_k, 
#         "eval_is_complete": True 
#     }

def expand_search_node(state: RAGAgentState):
    # 1. Scale up top_k parameter
    new_k = state["top_k"] + 3
    
    # 2. Extract current message list
    # current_messages = state["query"]
    
    # 3. Trim the last 2 messages (The AIMessage tool call and the ToolMessage response)
    # This leaves only the SystemMessage and the User's question
    # trimmed_messages = current_messages[:-2]
    # print("current\n",current_messages)
    # print("trimmed\n",trimmed_messages)
    
    print(f"🔄 Cleared incomplete tool context. Resetting history and upscaling to top_k={new_k}")
    
    return {
        # "query": trimmed_messages, 
        "top_k": new_k, 
        "eval_is_complete": True 
    }

def my_custom_router(state: RAGAgentState):
    # Inspect the last message sent by the LLM
    #print(state["query"])
    last_message = state["query"][-1]
    print("mycustom_router\n",last_message)
    # If the LLM wants to use a tool, it will populate 'tool_calls'
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    
    if state.get("eval_is_complete") is False and state.get("loop_count", 0) < 3:
        print(f"⚠️ Context incomplete! Escalating search footprint from top_k={state['top_k']} to {state['top_k'] + 3}")
        return "expand_search"
    # If no tool calls, we are done
    return "end"

toolnode = ToolNode(tools,messages_key="query")

rag_agent = StateGraph(RAGAgentState)
checkpointer = InMemorySaver()

rag_agent.add_node("llm_node",llm_node)
rag_agent.add_node("tool_node",toolnode)
rag_agent.add_node("evaluator_node", evaluator_node) # <-- Added
rag_agent.add_node("expand_search", expand_search_node) # <-- Added

rag_agent.add_edge(START,"llm_node")
# rag_agent.add_conditional_edges("llm_node",tools_condition,
#                             {"tools": "tool_node",  # Match your node name exactly
#         END: END})

rag_agent.add_conditional_edges("llm_node",my_custom_router,
                            {"call_tools": "tool_node",  # Match your node name exactly
        "end": END})

# rag_agent.add_edge("tool_node","llm_node")

# Tool execution sends data straight into our evaluator inspector node
rag_agent.add_edge("tool_node", "evaluator_node")

# Evaluator loops out to check if we loop back for more text or move to answer synthesis
rag_agent.add_conditional_edges(
    "evaluator_node",
    my_custom_router,
    {
        "expand_search": "expand_search",
        "end": "llm_node" # Return to brain so it synthesizes the final comprehensive answers
    }
)

rag_agent.add_edge("expand_search", "tool_node")

# rag_agent.add_edge("llm_node",END)
rag_agent_flow = rag_agent.compile(checkpointer=checkpointer)

print(rag_agent_flow.get_graph().draw_ascii())

config = {"configurable": {"thread_id": "xxx_session_001"}}
while True:
    user_input = input("You >")
    if len(user_input) ==0 :
        continue
    if user_input.lower() in ['bye','quit','exit'] :
        break
    
    
    init_prompt= [
    SystemMessage(content="""You are a document reading assistant.
                Before providing a final answer, explain your reasoning process:
            1. Acknowledge the user's request.
            2. State if you need to use a tool and why.
            3. Summarize what you found in the tool.
            4. Provide the final comprehensive answer.
                
                
                """) ,
    HumanMessage(content=f"{user_input}")
    ]
    # response = rag_agent_flow.invoke({"query":init_prompt})

    # print(response)
    for chunk in rag_agent_flow.stream({"query":init_prompt,
                                        "top_k":3 ,
                                        "loop_count": 0,
                                        "eval_is_complete": True
                                        },config=config):
            # print(chunk.items())
            for node_name, state_update in chunk.items():
                print(f"\n--- Node: {node_name} ---ooo")
                # This shows you the messages added by each node
                if "query" in state_update:
                    last_msg = state_update["query"][-1]

                    print(f"Content: {last_msg.content}")
                    if hasattr(last_msg, 'tool_calls'):
                        print(f"Tool Calls: {last_msg.tool_calls}")
                    if hasattr(last_msg, 'usage_metadata'):
                        print(f"Token Usage: {last_msg.usage_metadata}")


# result = retriever.invoke("first 2 packages")

# def format_doc(docs):
#     nlist=[]
#     for doc in docs:
#         nlist.append(doc.page_content)
#     return "\n\n".join(nlist)
# # print(result)
# parser = StrOutputParser()

# template = PromptTemplate(template="You are a project assitant . Answer based on this {result}",
#                           input_variables=['result'])  


# # chain = retriever | parser | template | model | parser

# chain = retriever | format_doc | parser | template | model | parser

# result = chain.invoke("List all the packages in requirement.txt")

# print(result)

