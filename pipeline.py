import sys
import re
from llama_index.core import Settings, PromptTemplate
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
import rag_comp
import config

# ... [LLMGuard Class remains the same as your code] ...
class LLMGuard:
    def __init__(self, llm):
        self.llm = llm
        self.taxonomy = config.SAFETY_TAXONOMY
        
    def check(self, query: str) -> tuple[bool, str]:
        if len(query.strip()) < 2: return False, "Query too short."
        if re.search(r"ignore previous|system prompt|jailbreak", query.lower()):
            return False, "Blocked by Static Filter."

        guard_prompt = f"{self.taxonomy}\nUser Input: \"{query}\"\nClassification:"
        
        try:
            response = self.llm.complete(guard_prompt).text.strip().lower()
            if "unsafe" in response:
                return False, f"Blocked by AI Guardrail: {response}"
            return True, "Safe"
        except Exception as e:
            print(f"[!] Guardrail Error: {e}")
            return True, "Guardrail Skipped"

CUSTOM_RAG_PROMPT = PromptTemplate(
    "You are a strict Logistics Assistant.\n"
    "Context information is provided below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Query: {query_str}\n"
    "Answer: "
)

def build_rag_pipeline():
    print("[-] Initializing Research-Backed Secure Pipeline...")
    
    embed_model = rag_comp.get_embedding_model()
    llm = rag_comp.get_llm()
    Settings.embed_model = embed_model
    Settings.llm = llm

    # 1. Get Retrievers
    vector_retriever = rag_comp.get_vector_retriever(embed_model)
    bm25_retriever = rag_comp.get_bm25_retriever()

    # 2. Configure Hybrid Search (with fallback)
    if bm25_retriever:
        print("    Configuring Hybrid Search (Vector + BM25)...")
        retrievers = [vector_retriever, bm25_retriever]
    else:
        print("    Configuring Vector Search Only (BM25 Skipped)...")
        retrievers = [vector_retriever]

    fusion_retriever = QueryFusionRetriever(
        retrievers,
        similarity_top_k=3,
        num_queries=1,
        mode="relative_score",
        use_async=False,
        verbose=False
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion_retriever,
        llm=llm,
        text_qa_template=CUSTOM_RAG_PROMPT
    )
    
    print("    Activating Llama Guard Taxonomy Layer...")
    guard = LLMGuard(llm)

    return query_engine, guard