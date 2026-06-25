import streamlit as st
from datetime import datetime
from langchain.messages import HumanMessage,SystemMessage
# from backend import PRACagent
# from newbackend import PRACagent
from flowwithoutllm import agent
import time

CONFIG = {"configurable": {"thread_id": "db2_session_001"}}

# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")

st.title("Search Agent")

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





# result = agent.invoke(init_state)

if user_input:
    st.session_state['message'].append({'user' : user_input})
    with st.chat_message('user'):
        st.write(user_input)
    
    
    # print(result)
    # last_message = result['messages'][-1].content
    user_prompt = HumanMessage(content=user_input)

    init_prompt = {
    "a" : 5,
    "b" : 10,
    "query" : user_prompt.content ,
    "operation" : "search" ,
    "oper_sum" : 0,
    "oper_mult" : 0,
    "oper_square " : 0
}

    # init_prompt = {"messages" : [system_prompt,user_prompt]}
    print(init_prompt)
    with st.chat_message('ai'):
        
        # st.text(last_message)
        # last_message= st.write_stream(
        #     chunk.content for chunk,metadata in PRACagent.stream(init_prompt,
        #                       config=CONFIG,
        #                       stream_mode='messages'))
        token_usage=[]
        def stream_wrapper() :
            chunks = agent.stream(init_prompt,
                                config=CONFIG,
                                stream_mode='messages')
            for chunk, metadata in chunks:
                # print(chunk)
                if chunk.content:
                    yield chunk.content
            # print(chunks)
            # yield chunks
            
                # if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                #     token_usage.append(f"-----NodeName-------{metadata["langgraph_node"]}")
                #     token_usage.append(chunk.usage_metadata)
                token_usage.append(metadata)
                    
                    
                
           
        last_message=st.write_stream(stream_wrapper())

        # print(last_message)
        
        st.session_state['message'].append({'ai' : [last_message,token_usage]})

                
        with st.expander("MetaData"):
            st.write(token_usage)

