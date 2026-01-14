import os
import pickle
import logging
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Modern LangChain v0.3+ Imports
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")

# --- 1. Initialize Index (Ensures cache exists on Render) ---
def initialize_index():
    # If the cache folder doesn't exist, run the builder
    if not os.path.exists('cache'):
        logger.info("Cache folder not found. Running build_index.py...")
        try:
            subprocess.run(["python", "build_index.py"], check=True)
            logger.info("Index built successfully!")
        except Exception as e:
            logger.error(f"Error building index: {e}")
    else:
        logger.info("Index found in cache.")

initialize_index()

# --- 2. Mail Config ---
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)
mail = Mail(app)

# --- 3. AI Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.6)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

# --- 4. Vector Store Loading ---
VECTOR_STORE_PATH = os.path.join("cache", "vector_store.pkl")

def get_retriever():
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            with open(VECTOR_STORE_PATH, "rb") as f:
                vector_store = pickle.load(f)
            return vector_store.as_retriever(search_kwargs={"k": 2})
        except Exception as e:
            logger.error(f"Failed to load pickle: {e}")
    return None

retriever = get_retriever()

# --- 5. Clean RAG Chain (No History) ---
# System prompt focuses only on the context provided by your data.txt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Premkumar AI Assistant. Use the context to answer. If not in context, say you don't know.\n\nContext: {context}"),
    ("human", "{input}")
])

document_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, document_chain) if retriever else None

# --- 6. Routes ---
@app.route('/')
def home(): 
    return render_template('home.html')

@app.route('/chatbot')
def chatbot(): 
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "Knowledge base not ready.", "status": 503})
    
    data = request.get_json()
    user_input = data.get('message', '')
    
    try:
        # Straightforward RAG call without memory variables
        response = rag_chain.invoke({"input": user_input})
        return jsonify({"response": response["answer"], "status": 200})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"response": "Sorry, I encountered an error.", "status": 500})

# --- 7. Deployment Entry Point ---
if __name__ == '__main__':
    # Bind to Render's dynamic port
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
