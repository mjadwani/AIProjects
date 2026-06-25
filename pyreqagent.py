from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser

embedding_model = OllamaEmbeddings(model="embeddinggemma:latest")
model = ChatOllama(model="gemma4:e4b",num_ctx=8192)
vectorstore = FAISS.load_local(
    folder_path="C:\\Users\\mjadwani\\Documents\\langgraphpractice\\idx_requirement",
    index_name="index",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True

)

retriever = vectorstore.as_retriever(search_type =  "similarity" ,search_kwargs={"k":3})

# result = retriever.invoke("first 2 packages")

def format_doc(docs):
    nlist=[]
    for doc in docs:
        nlist.append(doc.page_content)
    return "\n\n".join(nlist)
# print(result)
parser = StrOutputParser()

template = PromptTemplate(template="You are a project assitant . Answer based on this {result}",
                          input_variables=['result'])  


# chain = retriever | parser | template | model | parser

chain = retriever | format_doc | parser | template | model | parser

result = chain.invoke("List all the packages in requirement.txt")

print(result)

