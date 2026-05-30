import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import tiktoken
from datetime import datetime, timezone
from utils.helpers import now_iso

# Initialize a persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(
    name="newsops_knowledge",
    embedding_function=embedding_func
)

def add_document(doc_id: str, text: str, metadata: dict):
    """
    Chunk text into 500-token chunks with 50-token overlap using tiktoken.
    Add each chunk as a separate embedding with doc_id + chunk index.
    metadata keys required: domain, source, timestamp, session_id.
    """
    if not text:
        return

    # Use cl100k_base encoding
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunk_size = 500
    overlap = 50
    step = chunk_size - overlap
    
    chunks = []
    if len(tokens) <= chunk_size:
        chunks.append(text)
    else:
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Avoid trailing small chunks that are just overlap
            if i + chunk_size >= len(tokens):
                break

    ids = []
    documents = []
    metadatas = []
    
    for idx, chunk_text in enumerate(chunks):
        ids.append(f"{doc_id}_{idx}")
        documents.append(chunk_text)
        metadatas.append(metadata)
        
    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

def search_similar(query_text: str, domain: str, n_results: int = 5) -> list[dict]:
    """
    Query the collection filtered by metadata domain == domain.
    Return list of: { "text": chunk_text, "source": metadata.source,
      "score": distance, "session_id": metadata.session_id }
    """
    # If the collection is empty, collection.query might fail or return empty.
    # To be safe, check document count
    if collection.count() == 0:
        return []
        
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"domain": domain}
        )
    except Exception:
        return []
        
    ret = []
    if results and results.get("documents") and len(results["documents"]) > 0:
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(documents)
        
        for doc, meta, dist in zip(documents, metadatas, distances):
            meta_dict = meta if isinstance(meta, dict) else {}
            ret.append({
                "text": doc,
                "source": meta_dict.get("source"),
                "score": dist,
                "session_id": meta_dict.get("session_id")
            })
    return ret

def add_session_knowledge(session_id: str, domain: str, master_brief: dict):
    """
    Called after pipeline completes — stores the insight, facts, and
    context from that session for future retrieval.
    """
    doc_id = f"session_{session_id}"
    insight = master_brief.get("insight") or ""
    context = master_brief.get("context") or ""
    text = f"{insight} {context}".strip()
    
    metadata = {
        "domain": domain,
        "source": "past_analysis",
        "session_id": session_id,
        "timestamp": now_iso()
    }
    
    add_document(doc_id, text, metadata)

def get_collection_stats() -> dict:
    """
    Returns: { total_documents, domains_covered, oldest_entry, newest_entry }
    """
    total = collection.count()
    if total == 0:
        return {
            "total_documents": 0,
            "domains_covered": [],
            "oldest_entry": None,
            "newest_entry": None
        }
        
    all_data = collection.get(include=["metadatas"])
    metadatas = all_data.get("metadatas") or []
    
    domains = set()
    oldest = None
    newest = None
    
    for meta in metadatas:
        if isinstance(meta, dict):
            dom = meta.get("domain")
            if dom:
                domains.add(dom)
            ts = meta.get("timestamp")
            if ts:
                if oldest is None or ts < oldest:
                    oldest = ts
                if newest is None or ts > newest:
                    newest = ts
                    
    return {
        "total_documents": total,
        "domains_covered": list(domains),
        "oldest_entry": oldest,
        "newest_entry": newest
    }
