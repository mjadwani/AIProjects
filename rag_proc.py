import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# --- CONFIGURATION ---
PDF_PATH = "C:\\Users\\mjadwani\\Documents\\langgraphpractice\\db2z_13_instbook.pdf"  # Path to your manual
INDEX_SAVE_PATH = "faiss_db2zparm_index"
MODEL_NAME = "embeddinggemma:300m"
# zparm_pages= pages [40:510]
def create_or_update_index():
    # 1. Initialize Embeddings (Ollama must be running)
    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    # 2. Load the PDF
    if not os.path.exists(PDF_PATH):
        print(f"Error: Could not find {PDF_PATH}")
        return
    
    print(f"--- Loading PDF: {PDF_PATH} ---")
    loader = PyPDFLoader(PDF_PATH)
    raw_documents = loader.load()
    zparm_pages= raw_documents [40:510]

    # 3. Split into Chunks
    # We use a 1000/100 split to keep enough context for ZPARM definitions
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    documents = text_splitter.split_documents(zparm_pages)
    print(f"--- Created {len(documents)} chunks from PDF ---")

    # 4. Create Vector Store (FAISS)
    print("--- Generating Embeddings (This uses your Intel CPU) ---")
    vectorstore = FAISS.from_documents(documents, embeddings)

    # 5. Save locally for reuse
    vectorstore.save_local(INDEX_SAVE_PATH)
    print(f"--- Success! Index saved to {INDEX_SAVE_PATH} ---")

if __name__ == "__main__":
    create_or_update_index()