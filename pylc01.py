'''
sample program to learn chunking 
Use of RecursiveTextSplitter
'''
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import pprint
from langchain_ollama.embeddings import OllamaEmbeddings
# from langchain_text_splitters import Mar
# from pymupdf import p

embedding_model = OllamaEmbeddings(model="embeddinggemma:latest")
# loader= PyMuPDFLoader("db2z_13_instbook.pdf",extract_tables='markdown')

loader2 = TextLoader("requirements.txt",encoding='utf-16')

# docs= loader.load()
textdocs = loader2.load()
# print(docs[1])

# pprint.pp(textdocs[0].page_content)
splitter =RecursiveCharacterTextSplitter(
                            chunk_size = 100,
                            chunk_overlap = 2,
                            separators=["\n"]
                                )

chunks= splitter.split_documents(textdocs)

for chunk in chunks:
    if '\n' in chunk.page_content:
        chunk_page_content_list = chunk.page_content.split('\n')
        print(chunk_page_content_list)
        chunk.page_content = chunk_page_content_list[1]
        print(chunk.page_content)

pprint.pp(chunks)

vectorstore = FAISS.from_documents(chunks,embedding_model)

vectorstore.save_local("idx_requirement")

# query = "List all packages you can find."

# # query_embedding = FAISS.from_texts(texts=[query],embedding=embedding_model)

# retriever = vectorstore.as_retriever(search_type='similarity',search_kwargs={"k": 3})

# result = retriever.invoke(query)

# pprint.pp(result)
# print(loader)
# print(docs[351])
# print(docs[333])