
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
# import sys
# sys.path.append("C:\\Users\\mjadwani\\Documents\\langgraphpractice")

def get_retriever() :
    embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
    # r=model.invoke("What is Capital of India ?").content
    vectorstore = FAISS.load_local(
        "C:\\Users\\mjadwani\\Documents\\langgraphpractice\\faiss_db2zparm_index", 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_type='similarity',search_kwargs={"k": 3})
    
    return retriever

if __name__ == "__main__":
    print(type(get_retriever()))