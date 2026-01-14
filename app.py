import os
import pickle
import logging
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# --- LATEST LANGCHAIN IMPORTS (v0.3.x / v1.x compatible) ---
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
# These are the direct functional imports that avoid the .chains issue
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")

# --- 1. Automatic Index Builder ---
def ensure_index_exists():
    # Make sure the cache folder exists
    if not os.path.exists('cache'):
        os.makedirs('cache')
        
    path = "cache/vector_store.pkl"
    if not os.path.exists(path):
        logger.info("Vector store not found. Building now...")
        try:
            subprocess.run(["python", "build_index.py"], check=True)
        except Exception as e:
            logger.error(f"Build failed: {e}")

# Run the check
ensure_index_exists()

# --- 2. AI Setup ---
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"), 
    model_name="llama-3.1-8b-instant", 
    temperature=0.6
)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- 3. Load Retriever ---
def load_my_retriever():
    path = "cache/vector_store.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                vs = pickle.load(f)
            return vs.as_retriever(search_kwargs={"k": 2})
        except:
            return None
    return None

retriever = load_my_retriever()

# --- 4. Build Chain ---
system_prompt = "You are Premkumar's Assistant. Answer using this context: {context}"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# Functional approach to creating chains
if retriever:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
else:
    rag_chain = None

# --- 5. Routes ---
@app.route('/')
def home(): 
    return "Server is Running"

@app.route('/chatbot')
def chatbot_page(): 
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "System initializing, please wait...", "status": 503})
    
    try:
        data = request.get_json()
        user_msg = data.get('message', '')
        result = rag_chain.invoke({"input": user_msg})
        return jsonify({"response": result["answer"], "status": 200})
    except Exception as e:
        return jsonify({"response": str(e), "status": 500})

# --- 6. Render Port Binding ---
if __name__ == '__main__':
    # Force Render's port
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
