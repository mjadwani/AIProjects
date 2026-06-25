from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.messages import SystemMessage,HumanMessage
import operator
from langgraph.checkpoint.memory import InMemorySaver

embedding_model = OllamaEmbeddings(model="embeddinggemma:latest")
model = ChatOllama(model="gemma4:e4b",num_ctx=8192)
vectorstore = FAISS.load_local(
    folder_path="C:\\Users\\mjadwani\\Documents\\langgraphpractice\\idx_requirement",
    index_name="index",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True

)

retriever = vectorstore.as_retriever(search_type =  "similarity" ,search_kwargs={"k":3})

@tool
def rag_tool(query :str ) -> str :
    """
    Tool purpose is to provide response to input query 
    by referencing the local rag knowledge which requirement.txt file .
    query is input parameter and is not optional
    """
    result_rag = retriever.invoke(query)
    content = [doc.page_content for doc in result_rag]
    return {
        "query" : query ,
        "content" : content
    }

tools= [rag_tool]

model_with_tools= model.bind_tools(tools)

class RAGAgentState(TypedDict):
    query : Annotated[list,operator.add]

def llm_node(state: RAGAgentState):
    response = model_with_tools.invoke(state["query"])
    return {"query" : [response]}

def my_custom_router(state: RAGAgentState):
    # Inspect the last message sent by the LLM
    #print(state["query"])
    last_message = state["query"][-1]
    
    # If the LLM wants to use a tool, it will populate 'tool_calls'
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    
    # If no tool calls, we are done
    return "end"

toolnode = ToolNode(tools,messages_key="query")

rag_agent = StateGraph(RAGAgentState)
checkpointer = InMemorySaver()

rag_agent.add_node("llm_node",llm_node)
rag_agent.add_node("tool_node",toolnode)

rag_agent.add_edge(START,"llm_node")
# rag_agent.add_conditional_edges("llm_node",tools_condition,
#                             {"tools": "tool_node",  # Match your node name exactly
#         END: END})

rag_agent.add_conditional_edges("llm_node",my_custom_router,
                            {"call_tools": "tool_node",  # Match your node name exactly
        "end": END})

rag_agent.add_edge("tool_node","llm_node")


# rag_agent.add_edge("llm_node",END)

rag_agent_flow = rag_agent.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "xxx_session_001"}}
init_prompt= [
SystemMessage(content="""You are a document reading assistant.
              Before providing a final answer, explain your reasoning process:
        1. Acknowledge the user's request.
        2. State if you need to use a tool and why.
        3. Summarize what you found in the tool.
        4. Provide the final comprehensive answer.
              
              
              """) ,
HumanMessage(content="Which are langchain related packages available ?")
]
# response = rag_agent_flow.invoke({"query":init_prompt})

# print(response)
for chunk in rag_agent_flow.stream({"query":init_prompt},config=config):
        # print(chunk.items())
        for node_name, state_update in chunk.items():
            print(f"\n--- Node: {node_name} ---")
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

