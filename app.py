import os
import json
import pickle
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Groq & HuggingFace Imports
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
mail = Mail(app)

# --- Configuration Constants ---
DOCUMENT_PATH = "data.txt"
CACHE_DIR = "cache"
VECTOR_STORE_PATH = os.path.join(CACHE_DIR, "vector_store.pkl")
INDEX_META_PATH = os.path.join(CACHE_DIR, "index_meta.json")
# Using your requested models
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant" # Note: If 'compound-mini' is a private model, use its specific ID here

# Initialize Groq LLM
llm = ChatGroq(
    temperature=0.7,
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name=GROQ_MODEL
)

# Initialize Embeddings (Required to load the vector store correctly)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

def load_cached_vector_store():
    if not os.path.exists(VECTOR_STORE_PATH):
        return None
    try:
        with open(VECTOR_STORE_PATH, "rb") as f:
            vector_store = pickle.load(f)
        return vector_store.as_retriever(search_kwargs={"k": 2})
    except Exception as e:
        app.logger.error(f"Failed to load vector store: {e}")
        return None

# Initialize Chains
retriever = load_cached_vector_store()

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are Premkumar AI Assistant, a friendly and intelligent chatbot built to assist users based on the data provided only.\n"
     "Context:\n{context}\n\n"
     "Conversation History:\n{history}\n\n"
     "IMPORTANT: Do NOT mention or repeat: job title (AI Engineer, Data Scientist), areas of expertise (ML, DL, NLP, RAG), tools (Power BI, SQL), experience duration, or current employer. If asked, say information is unavailable."
    ),
    ("human", "{input}")
])

document_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, document_chain) if retriever else None

memory = ConversationBufferMemory(memory_key="history", input_key="input", output_key="answer", return_messages=True)

# --- Routes ---
@app.route('/')
def home(): return render_template('home.html')

@app.route('/chatbot')
def chatbot(): return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "Knowledge base not ready. Run build_index.py.", "status": 503})
    
    data = request.get_json()
    user_input = data.get('message', '')
    
    try:
        history = memory.load_memory_variables({})["history"]
        response = rag_chain.invoke({"input": user_input, "history": history})
        memory.save_context({"input": user_input}, {"answer": response["answer"]})
        return jsonify({"response": response["answer"], "status": 200})
    except Exception as e:
        return jsonify({"response": "Internal Error", "status": 500})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # ... (Keep your existing contact logic here)
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
