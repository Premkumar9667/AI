import os
import json
import pickle
import logging
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Optional: GOOGLE_API_KEY should be provided via .env when using Gemini backend.
# (Removed hardcoded key for security.)

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    max_tokens=512
)

# Read the text file
def load_text_file(file_path="data.txt"):
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            content = file.read()
        return [Document(page_content=content, metadata={"source": file_path})]
    except FileNotFoundError:
        app.logger.error(f"Error: {full_path} not found in the server directory.")
        return []
    except Exception as e:
        app.logger.error(f"Error loading {full_path}: {str(e)}")
        return []

DOCUMENT_PATH = "data.txt"
CACHE_DIR = "cache"
VECTOR_STORE_PATH = os.path.join(CACHE_DIR, "vector_store.pkl")
INDEX_META_PATH = os.path.join(CACHE_DIR, "index_meta.json")
BACKEND = os.getenv("EMBEDDING_BACKEND", "local").lower()
EMBED_MODEL_NAME = (
    "models/embedding-001" if BACKEND == "gemini" else os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
)

documents = load_text_file(DOCUMENT_PATH)
retriever = None  # Will be loaded from cache if available

def load_cached_vector_store():
    """Attempt to load cached vector store if up-to-date.

    Returns:
        retriever or None
    """
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(INDEX_META_PATH):
        app.logger.info("Vector store cache not found. Run build_index.py to create it.")
        return None

    # Validate modification time of document
    try:
        with open(INDEX_META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        doc_mtime_cached = meta.get("documents", {}).get(DOCUMENT_PATH, {}).get("mtime")
        current_mtime = os.path.getmtime(DOCUMENT_PATH) if os.path.exists(DOCUMENT_PATH) else None
        if not current_mtime or doc_mtime_cached != current_mtime:
            app.logger.warning("Cached index is stale (document changed). Re-run build_index.py.")
            return None
        if meta.get("embedding_model") != EMBED_MODEL_NAME:
            app.logger.warning("Embedding model changed. Re-run build_index.py.")
            return None
        if meta.get("backend") != BACKEND:
            app.logger.warning("Embedding backend changed. Re-run build_index.py.")
            return None
        with open(VECTOR_STORE_PATH, "rb") as f:
            vector_store = pickle.load(f)
        # Convert to retriever
        return vector_store.as_retriever(search_kwargs={"k": 1})
    except Exception as e:
        app.logger.error(f"Failed to load cached vector store: {e}")
        return None

# Lazy load retriever
retriever = load_cached_vector_store()

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are Premkumar AI Assistant, a friendly and intelligent chatbot built to assist users based on the data provided in the uploaded text file only.\n"
     "Always stay within the bounds of the provided context. If a user asks something not covered in the context, respond politely that the information is unavailable.\n"
     "Never guess or hallucinate. Use bullet points or structured answers where appropriate.\n"
     "\nContext:\n{context}\n\n"
     "Conversation History:\n{history}\n\n"
     "IMPORTANT: Do NOT mention or repeat the following details in your answers, even if asked directly: job title (AI Engineer, Data Scientist), areas of expertise (machine learning, deep learning, NLP, RAG, LLMs, vector databases like Qdrant), data analysis tools (Power BI, Excel, SQL), experience duration (4+ months), project/technology counts (3+ AI projects, 5+ technologies), or current employer (Digidara Technologies). If a user asks about these, politely state that this information is not available."
    ),
    ("human", "{input}")
])


# Create the document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# Only create the retrieval chain if retriever is available
rag_chain = None
if retriever is not None:
    rag_chain = create_retrieval_chain(retriever, document_chain)

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="history",
    input_key="input",
    output_key="answer",
    return_messages=True
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/work')
def work():
    return render_template('work.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        purpose = request.form.get('purpose')
        description = request.form.get('description')
        
        if not all([name, email, phone, purpose]):
            flash('Please fill in all required fields.', 'error')
            return render_template('contact.html')
        
        # Try to send email, but don't fail if email is not configured
        try:
            if os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD'):
                # Send email
                msg = Message(
                    subject=f'Portfolio Contact: {purpose}',
                    recipients=[os.environ.get('MAIL_USERNAME')],
                    body=f'''
New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Purpose: {purpose}
Description: {description if description else 'No description provided'}

Please respond promptly to this inquiry.
                    '''
                )
                mail.send(msg)
                flash('Message sent successfully! Thank you for reaching out.', 'success')
            else:
                # Log the contact form submission instead
                app.logger.info(f'Contact form submission - Name: {name}, Email: {email}, Phone: {phone}, Purpose: {purpose}')
                flash('Thank you for your message! I have received your contact information and will get back to you soon.', 'success')
            
            return redirect(url_for('contact'))
            
        except Exception as e:
            app.logger.error(f'Error sending email: {str(e)}')
            # Still show success to user, but log the submission
            app.logger.info(f'Contact form submission (email failed) - Name: {name}, Email: {email}, Phone: {phone}, Purpose: {purpose}')
            flash('Thank you for your message! I have received your contact information and will get back to you soon.', 'success')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/download-resume')
def download_resume():
    return send_from_directory('static/resume', 'resume.pdf', as_attachment=True)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not documents:
            app.logger.error("No documents loaded; data.txt likely missing.")
            return jsonify({"response": "Error: data.txt not found in the server directory.", "status": 500}), 500

        if retriever is None or rag_chain is None:
            return jsonify({"response": "Knowledge base not indexed yet. Please run build_index.py once to generate embeddings.", "status": 503}), 503

        data = request.get_json()
        user_input = data.get('message', '')

        if not user_input:
            return jsonify({"response": "Please provide a message.", "status": 400}), 400

        # Load conversation history
        history = memory.load_memory_variables({})["history"]

        # Process the input through the RAG chain
        response = rag_chain.invoke({
            "input": user_input,
            "history": history
        })

        # Update conversation memory
        memory.save_context({"input": user_input}, {"answer": response["answer"]})

        return jsonify({"response": response["answer"], "status": 200})
    except Exception as e:
        app.logger.error(f"Error in /chat endpoint: {str(e)}")
        return jsonify({"response": "Internal server error.", "status": 500}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

