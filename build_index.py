import os
import json
import pickle
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Constants
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
DOCUMENT_PATH = "data.txt"
CACHE_DIR = "cache"
VECTOR_STORE_PATH = os.path.join(CACHE_DIR, "vector_store.pkl")
INDEX_META_PATH = os.path.join(CACHE_DIR, "index_meta.json")
SCRIPT_VERSION = 3  # Bumped for Groq/HF migration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_index")

def load_text_file(file_path: str) -> list[Document]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [Document(page_content=content, metadata={"source": file_path})]

def needs_rebuild() -> bool:
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(INDEX_META_PATH):
        return True
    try:
        with open(INDEX_META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        current_mtime = os.path.getmtime(DOCUMENT_PATH) if os.path.exists(DOCUMENT_PATH) else None
        
        return (meta.get("script_version") != SCRIPT_VERSION or 
                meta.get("embedding_model") != EMBED_MODEL_NAME or 
                meta.get("documents", {}).get(DOCUMENT_PATH, {}).get("mtime") != current_mtime)
    except:
        return True

def build_index():
    docs = load_text_file(DOCUMENT_PATH)
    logger.info(f"Generating local embeddings using {EMBED_MODEL_NAME}...")
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vector_store = InMemoryVectorStore.from_documents(docs, embeddings)

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(vector_store, f)

    meta = {
        "script_version": SCRIPT_VERSION,
        "embedding_model": EMBED_MODEL_NAME,
        "documents": {
            DOCUMENT_PATH: {
                "mtime": os.path.getmtime(DOCUMENT_PATH),
                "size": os.path.getsize(DOCUMENT_PATH)
            }
        }
    }
    with open(INDEX_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    logger.info("Index build complete.")

if __name__ == "__main__":
    if needs_rebuild():
        build_index()
    else:
        logger.info("Index is up to date.")
