import os
import pickle
import logging
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# MODERN IMPORTS - ONLY THE ESSENTIALS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")

# --- 1. ENSURE DATA EXISTS ---
def ensure_index():
    if not os.path.exists('cache'):
        os.makedirs('cache')
    
    path = "cache/vector_store.pkl"
    if not os.path.exists(path):
        logger.info("Building knowledge base...")
        try:
            subprocess.run(["python", "build_index.py"], check=True)
        except Exception as e:
            logger.error(f"Build failed: {e}")

ensure_index()

# --- 2. AI CONFIGURATION ---
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"), 
    model_name="llama-3.1-8b-instant", 
    temperature=0.6
)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- 3. LOAD RETRIEVER ---
def load_retriever():
    path = "cache/vector_store.pkl"
    if os.path.exists(path):
        with open(path, "rb") as f:
            vs = pickle.load(f)
        return vs.as_retriever(search_kwargs={"k": 2})
    return None

retriever = load_retriever()

# --- 4. THE CHATBOT LOGIC (Modern LCEL Way) ---
# This replaces "create_retrieval_chain" entirely
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# This is the "Chain" - notice we don't import 'langchain.chains'
if retriever:
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
else:
    rag_chain = None

# --- 5. ROUTES ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not rag_chain:
        return jsonify({"response": "System is booting up. Please wait.", "status": 503})
    
    try:
        data = request.get_json()
        user_msg = data.get('message', '')
        # Simple invoke
        answer = rag_chain.invoke(user_msg)
        return jsonify({"response": answer, "status": 200})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"response": "I'm having trouble thinking right now.", "status": 500})

# --- 6. RENDER PORT BINDING ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
