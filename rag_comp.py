import os
import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter 
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.retrievers.bm25 import BM25Retriever
import config

def get_embedding_model():
    print(f"[--] Loading Embedding Model: {config.EMBED_MODEL_NAME}...")
    return HuggingFaceEmbedding(model_name=config.EMBED_MODEL_NAME)

def get_llm():
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("[!] GOOGLE_API_KEY is missing.")
    
    return Gemini(model=config.LLM_MODEL_NAME, temperature=0.5)

def get_vector_retriever(embed_model):
    print(f"    Connecting to ChromaDB at {config.INDEX_DIR}...")
    
    # Safety check if index folder exists
    if not os.path.exists(config.INDEX_DIR):
        print("[!] Index directory not found. Did S3 download fail?")
        # Return None or handle strictly depending on preference
        
    db = chromadb.PersistentClient(path=config.INDEX_DIR)
    chroma_collection = db.get_or_create_collection(config.CHROMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    vector_index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    return vector_index.as_retriever(similarity_top_k=5)

def get_bm25_retriever():
    """
    Attempts to build BM25 retriever. If raw files are missing, returns None.
    """
    print("    Checking raw documents for Keyword Index (BM25)...")
    
    if not os.path.exists(config.RAW_DATA_DIR) or not os.listdir(config.RAW_DATA_DIR):
        print("    [!] No raw data found. Skipping BM25.")
        return None
    
    documents = SimpleDirectoryReader(config.RAW_DATA_DIR).load_data()
    
    print("    Splitting text into nodes...")
    splitter = SentenceSplitter(chunk_size=256, chunk_overlap=32)
    nodes = splitter.get_nodes_from_documents(documents)
    
    print(f"    Building BM25 Index with {len(nodes)} nodes...")
    return BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=5
    )