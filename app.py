import os
import json
import pickle
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Groq & HF Imports
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
# from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")
import os
import subprocess

# This runs BEFORE the Flask app starts
def initialize_index():
    # Check if your index folder (e.g., 'faiss_index') already exists
    if not os.path.exists('faiss_index'):
        print("Index not found. Running build_index.py...")
        try:
            # Runs your script as if you typed it in the terminal
            subprocess.run(["python", "build_index.py"], check=True)
            print("Index built successfully!")
        except Exception as e:
            print(f"Error building index: {e}")
    else:
        print("Index already exists. Skipping build.")

# Call the function
initialize_index()

# ... Your existing app = Flask(__name__) code ...

# --- Mail Config ---
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)
mail = Mail(app)

# --- AI Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.6)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

# --- Vector Store Loading ---
VECTOR_STORE_PATH = "cache/vector_store.pkl"

def get_retriever():
    if os.path.exists(VECTOR_STORE_PATH):
        with open(VECTOR_STORE_PATH, "rb") as f:
            vector_store = pickle.load(f)
        return vector_store.as_retriever(search_kwargs={"k": 2})
    return None

retriever = get_retriever()

# --- Prompt & Chain ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Premkumar AI Assistant. Use the context to answer. If not in context, say you don't know.\n\nContext: {context}\n\nHistory: {history}"),
    ("human", "{input}")
])

document_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, document_chain) if retriever else None
# memory = ConversationBufferMemory(memory_key="history", input_key="input", output_key="answer", return_messages=True)

# --- Routes ---
@app.route('/')
def home(): return render_template('home.html')

@app.route('/chatbot')
def chatbot(): return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "Knowledge base not initialized. Run build_index.py.", "status": 503})
    
    data = request.get_json()
    user_input = data.get('message', '')
    
    try:
        history = memory.load_memory_variables({})["history"]
        response = rag_chain.invoke({"input": user_input, "history": history})
        memory.save_context({"input": user_input}, {"answer": response["answer"]})
        return jsonify({"response": response["answer"], "status": 200})
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({"response": "Sorry, I encountered an error.", "status": 500})

# ... (all your imports and logic)

if __name__ == '__main__':
    # Render provides a PORT environment variable. 
    # Use 0.0.0.0 to allow external traffic.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



