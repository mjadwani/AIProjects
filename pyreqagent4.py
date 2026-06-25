import json
import operator
from typing import TypedDict, Annotated, Dict, Any, List
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langgraph.prebuilt import ToolNode

# =====================================================================
# 1. Initialization & Core Configurations
# =====================================================================
# Main model with an expanded context window for handling multiple chunks
model = ChatOllama(model="gemma4:e4b", num_ctx=8192)

def retriever_block(top_k_val: int):
    """Initializes and returns the FAISS vector retriever with dynamic top_k."""
    embedding_model = OllamaEmbeddings(model="embeddinggemma:latest")
    vectorstore = FAISS.load_local(
        folder_path="C:\\Users\\mjadwani\\Documents\\langgraphpractice\\faiss_db2zparm_index",
        index_name="index",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k_val})

# =====================================================================
# 2. Tool Definition
# =====================================================================
@tool
def rag_tool(query: str, state: Annotated[dict, "InjectedState"]) -> dict:
    """
    Query the local Db2 zparm documentation index to retrieve technical configuration details.
    """
    # Read dynamic top_k directly from the graph state
    current_k = state.get("top_k", 3)
    print(f"\n[TOOL RUNTIME] Executing vector search for '{query}' with top_k={current_k}...")
    
    retriever = retriever_block(current_k)
    result_rag = retriever.invoke(query)
    content = [doc.page_content for doc in result_rag]
    
    return {
        "query": query,
        "content": content
    }

tools = [rag_tool]
model_with_tools = model.bind_tools(tools)

# =====================================================================
# 3. State Schema
# =====================================================================
class RAGAgentState(TypedDict):
    query: Annotated[list, operator.add]  # Appends chat history
    top_k: int                           # Controls retrieval scale dynamically
    loop_count: int                      # Built-in circuit breaker
    eval_is_complete: bool               # Tracks evaluator decision flag

# =====================================================================
# 4. Processing Graph Nodes
# =====================================================================
def llm_node(state: RAGAgentState):
    print("\n--- Node: llm_node ---")
    response = model_with_tools.invoke(state["query"])
    return {"query": [response]}

def evaluator_node(state: RAGAgentState):
    print("\n--- Node: evaluator_node ---")
    
    # Extract the tool output from the latest state message
    last_msg = state["query"][-1]
    retrieved_context = last_msg.content  
    
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
    
    # Dedicated evaluation call running with a deterministic temperature of 0.0
    response = model.invoke(
        [HumanMessage(content=eval_prompt)],
        options={"temperature": 0.0, "format": "json"}
    )
    
    try:
        eval_data = json.loads(response.content)
        print(f"[EVALUATION VERDICT]: {eval_data}")
        is_complete = eval_data.get("is_complete", True)
    except Exception:
        print("[EVALUATION ERROR] Failed to parse evaluation JSON. Forcing progression.")
        is_complete = True
        
    return {
        "eval_is_complete": is_complete,
        "loop_count": state["loop_count"] + 1
    }

def expand_search_node(state: RAGAgentState):
    """Node that increments search footprint when content is missing."""
    new_k = state["top_k"] + 3
    return {
        "top_k": new_k, 
        "eval_is_complete": True  # Reset flag to clear router state tracking
    }

# =====================================================================
# 5. Dedicated Routing Logic
# =====================================================================
def routing_llm_output(state: RAGAgentState):
    """Router 1: Inspects LLM output to determine if tool usage is requested."""
    last_message = state["query"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    return "end"

def routing_evaluator_output(state: RAGAgentState):
    """Router 2: Inspects context completeness flag to expand search or conclude."""
    if state.get("eval_is_complete") is False and state.get("loop_count", 0) < 3:
        print(f"⚠️ Context flagged as incomplete. Scaling lookup footprint...")
        return "expand_search"
    
    print("✅ Context declared sufficient or loop ceiling hit. Finalizing answer.")
    return "finalize"

# =====================================================================
# 6. Graph Compilation & Wiring
# =====================================================================
toolnode = ToolNode(tools, messages_key="query")
rag_agent = StateGraph(RAGAgentState)
checkpointer = InMemorySaver()

# Map Processing Blocks
rag_agent.add_node("llm_node", llm_node)
rag_agent.add_node("tool_node", toolnode)
rag_agent.add_node("evaluator_node", evaluator_node)
rag_agent.add_node("expand_search", expand_search_node)

# Set Graph Interconnections
rag_agent.add_edge(START, "llm_node")

# Conditional Routing 1: Execute Tool vs End
rag_agent.add_conditional_edges(
    "llm_node",
    routing_llm_output,
    {
        "call_tools": "tool_node",
        "end": END
    }
)

# Tool executions funnel into the text analyzer node
rag_agent.add_edge("tool_node", "evaluator_node")

# Conditional Routing 2: Evaluate and Route Loop
rag_agent.add_conditional_edges(
    "evaluator_node",
    routing_evaluator_output,
    {
        "expand_search": "expand_search",
        "finalize": "llm_node"  # Returns back to LLM to write the final summary
    }
)

# Route expansion adjustments straight back into tool execution for efficiency
rag_agent.add_edge("expand_search", "tool_node")

rag_agent_flow = rag_agent.compile(checkpointer=checkpointer)

# =====================================================================
# 7. User Interaction Execution Loop
# =====================================================================
config = {"configurable": {"thread_id": "db2_mainframe_session_001"}}

print("\n--- Db2 z/OS Parameter Agent Initialized ---")
print("Ask a question about system parameters. Type 'exit' to quit.\n")

while True:
    user_input = input("You > ")
    if user_input.lower() in ['bye', 'quit', 'exit']:
        break
    if len(user_input.strip()) == 0:
        continue
        
    init_prompt = [
        SystemMessage(content=(
            "You are a document reading assistant for z/OS Db2 subsystem parameters (zparms).\n"
            "Explain your process directly:\n"
            "1. State what parameter you are looking up.\n"
            "2. Detail what was found in the documentation.\n"
            "3. Deliver a comprehensive final answer.\n"
        )),
        HumanMessage(content=user_input)
    ]
    
    # Prime initial graph state params
    inputs = {
        "query": init_prompt,
        "top_k": 3,
        "loop_count": 0,
        "eval_is_complete": True
    }
    
    # Process graph and stream text token execution updates
    for chunk in rag_agent_flow.stream(inputs, config=config):
        for node_name, state_update in chunk.items():
            if "query" in state_update:
                last_msg = state_update["query"][-1]
                if last_msg.content and isinstance(last_msg, AIMessage):
                    print(f"\n[{node_name} Final Answer Output]:\n{last_msg.content}")