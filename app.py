import os
import pickle
import logging
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# CORRECT MODERN IMPORTS (v0.3.x+)
import langchain
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
# We import these directly from the sub-packages to avoid the ModuleNotFoundError
from langchain.chains import retrieval
from langchain.chains import combine_documents
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")

# --- 1. FORCE BUILD INDEX ON STARTUP ---
# This ensures that even if Render wipes the folder, we build it immediately.
def ensure_index():
    cache_path = os.path.join(os.getcwd(), 'cache')
    index_file = os.path.join(cache_path, 'vector_store.pkl')
    
    if not os.path.exists(index_file):
        logger.info("Index file missing. Running build_index.py...")
        try:
            # This runs your build script automatically
            subprocess.run(["python", "build_index.py"], check=True)
            logger.info("Build script finished successfully.")
        except Exception as e:
            logger.error(f"Failed to run build_index.py: {e}")

ensure_index()

# --- 2. AI CONFIGURATION ---
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"), 
    model_name="llama-3.1-8b-instant", 
    temperature=0.6
)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- 3. LOAD RETRIEVER ---
def get_retriever():
    path = "cache/vector_store.pkl"
    if os.path.exists(path):
        with open(path, "rb") as f:
            vector_store = pickle.load(f)
        return vector_store.as_retriever(search_kwargs={"k": 2})
    return None

retriever = get_retriever()

# --- 4. CREATE RAG CHAIN ---
system_prompt = "You are Premkumar's AI. Answer using context: {context}"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# Use the loaded sub-modules to create the chain
combine_docs_chain = combine_documents.create_stuff_documents_chain(llm, prompt)
rag_chain = retrieval.create_retrieval_chain(retriever, combine_docs_chain) if retriever else None

# --- 5. ROUTES ---
@app.route('/')
def home(): return render_template('home.html')

@app.route('/chatbot')
def chatbot(): return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "Knowledge base not ready. Please refresh in a minute.", "status": 503})
    
    try:
        user_input = request.get_json().get('message', '')
        response = rag_chain.invoke({"input": user_input})
        return jsonify({"response": response["answer"], "status": 200})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"response": "Error processing request.", "status": 500})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
