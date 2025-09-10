"""One-time (or on-demand) embedding/index builder.

Usage:
    python build_index.py

Rebuild triggers:
 - data.txt modified time changes
 - embedding model name changes
 - script version increments

Outputs:
 - cache/vector_store.pkl : pickled InMemoryVectorStore
 - cache/index_meta.json  : metadata with mtime + model
"""
import os
import json
import pickle
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

# Backends:
#  - local (default): HuggingFace sentence-transformers/all-MiniLM-L6-v2
#  - gemini: Google Generative AI embeddings API
BACKEND = os.getenv("EMBEDDING_BACKEND", "local").lower()
HF_MODEL_DEFAULT = "sentence-transformers/all-MiniLM-L6-v2"
HF_MODEL = os.getenv("HF_EMBEDDING_MODEL", HF_MODEL_DEFAULT)

if BACKEND == "gemini":
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore
else:
    # local backend
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Missing dependency: install sentence-transformers and langchain-community for local embeddings.") from e

SCRIPT_VERSION = 2  # bump when logic changes
EMBED_MODEL_NAME = (
    "models/embedding-001" if BACKEND == "gemini" else HF_MODEL
)
DOCUMENT_PATH = "data.txt"
CACHE_DIR = "cache"
VECTOR_STORE_PATH = os.path.join(CACHE_DIR, "vector_store.pkl")
INDEX_META_PATH = os.path.join(CACHE_DIR, "index_meta.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_index")

load_dotenv()

os.environ.setdefault("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))


def load_text_file(file_path: str) -> list[Document]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found. Cannot build index.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [Document(page_content=content, metadata={"source": file_path})]


def needs_rebuild() -> bool:
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(INDEX_META_PATH):
        logger.info("Cache missing; need to build index.")
        return True
    try:
        with open(INDEX_META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("script_version") != SCRIPT_VERSION:
            logger.info("Script version changed; rebuilding index.")
            return True
        if meta.get("embedding_model") != EMBED_MODEL_NAME:
            logger.info("Embedding model changed; rebuilding index.")
            return True
        doc_meta = meta.get("documents", {}).get(DOCUMENT_PATH)
        current_mtime = os.path.getmtime(DOCUMENT_PATH) if os.path.exists(DOCUMENT_PATH) else None
        if not doc_meta or doc_meta.get("mtime") != current_mtime:
            logger.info("Document mtime changed; rebuilding index.")
            return True
        logger.info("Cached index is fresh; no rebuild needed.")
        return False
    except Exception as e:
        logger.warning(f"Failed to validate cache metadata: {e}; rebuilding.")
        return True


def build_index():
    docs = load_text_file(DOCUMENT_PATH)
    logger.info(f"Loaded {len(docs)} document(s). Generating embeddings with {EMBED_MODEL_NAME}...")
    if BACKEND == "gemini":
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL_NAME)
    else:
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vector_store = InMemoryVectorStore.from_documents(docs, embeddings)

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(vector_store, f)

    meta = {
        "script_version": SCRIPT_VERSION,
    "embedding_model": EMBED_MODEL_NAME,
    "backend": BACKEND,
        "documents": {
            DOCUMENT_PATH: {
                "mtime": os.path.getmtime(DOCUMENT_PATH),
                "size": os.path.getsize(DOCUMENT_PATH)
            }
        },
        "built_at": os.path.getmtime(VECTOR_STORE_PATH)
    }
    with open(INDEX_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    logger.info("Index build complete and cached.")


if __name__ == "__main__":
    if needs_rebuild():
        build_index()
    else:
        logger.info("Nothing to do.")
