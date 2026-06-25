import tiktoken
from langchain_core.messages import HumanMessage,SystemMessage,BaseMessage
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from typing import TypedDict,Annotated,List
from pydantic import BaseModel, Field
import operator


model = ChatOllama(model="gemma4:e4b" ,
                    temperature=0,num_ctx=8192)

class ChatState(TypedDict) :
    # messages : Annotated[List[BaseMessage],operator.add]
    messages : list

class QuizAnswer(BaseModel):
    answer: str = Field(description="The capital city")
    confidence: float = Field(description="Score between 0 and 1")

structmodel = model.with_structured_output(QuizAnswer,include_raw=True) 

def get_token_count(messages : str):
    encoding = tiktoken.get_encoding("cl100k_base")
    text = messages
    return len(encoding.encode(text))

def chatnode(state: ChatState):
     response = structmodel.invoke(state['messages'])
     print(response)
     return {"messages" : [response] }

# print(get_token_count("ZPARM"))
# print(get_token_count("zparm"))
graph = StateGraph(ChatState)
graph.add_node("chatnode",chatnode)
graph.add_edge(START,"chatnode")
graph.add_edge("chatnode",END)

simplechattool = graph.compile()

if __name__ == '__main__':
    messages = [
    SystemMessage(content= "We are playing Quiz ") ,
    HumanMessage(content="What is the capital of India?")
    ]

    # total_token = get_token_count(system_prompt.content) + get_token_count(user_prompt.content)
    # print(f"Input_token_count:{total_token}")
    # response = simplechattool.invoke({"messages": messages})
    for chunk in simplechattool.stream({"messages": messages},stream_mode="updates"):
        # print(chunk.items())
        for node_name, state_update in chunk.items():
            print(node_name)
            print(state_update)
            print(f"\n--- [Progress] Node {node_name} finished ---")
        # You can inspect the update here
    # print(response['messages'][-1].content)
    # print(response['messages'][-1].usage_metadata)
    
    # print(type(response))
    # for x in response.keys():
    #     print(x)
    # print(response['messages'])
    # print(type(response['messages']))
    # total_token_output =get_token_count(response.co)