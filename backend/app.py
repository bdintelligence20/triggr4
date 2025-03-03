import os
import uuid
import json
import base64
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

# -------------------------------
# Load External Service Credentials from Environment Variables
# -------------------------------

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

# Pinecone Credentials and Index Name
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

# Anthropic (Claude 3.5 Sonnet) API Key
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# OpenAI API Key for Embeddings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Firebase and GCS Credentials (Base64-encoded strings)
firebase_cred_b64 = os.environ.get("FIREBASE_CRED_B64")
gcs_cred_b64 = os.environ.get("GCS_CRED_B64")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")  # should be "knowledge-hub-files"

if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM and
        PINECONE_API_KEY and PINECONE_INDEX_NAME and
        ANTHROPIC_API_KEY and OPENAI_API_KEY and
        firebase_cred_b64 and gcs_cred_b64 and GCS_BUCKET_NAME):
    raise Exception("One or more required environment variables are missing.")

# Decode the Base64 encoded credentials into proper JSON strings
firebase_cred_json_str = base64.b64decode(firebase_cred_b64).decode("utf-8")
gcs_cred_json_str = base64.b64decode(gcs_cred_b64).decode("utf-8")

# -------------------------------
# Initialize External Services
# -------------------------------

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore
firebase_cred_info = json.loads(firebase_cred_json_str)
firebase_admin.initialize_app(credentials.Certificate(firebase_cred_info))
db = firestore.client()

# Updated Pinecone Initialization using the new SDK
from pinecone import Pinecone
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    host="https://knowledge-hub-vectors-d6aehd0.svc.gcp-us-central1-4a9f.pinecone.io"
)
index = pc.Index(PINECONE_INDEX_NAME)

# Twilio Client
from twilio.rest import Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Cloud Storage
from google.cloud import storage
gcs_client = storage.Client.from_service_account_info(json.loads(gcs_cred_json_str))
bucket = gcs_client.bucket(GCS_BUCKET_NAME)

# OpenAI
import openai
openai.api_key = OPENAI_API_KEY

# Anthropic
import anthropic
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Libraries for text extraction
import PyPDF2
import docx2txt

# -------------------------------
# Flask App Configuration
# -------------------------------
app = Flask(__name__)
CORS(app, origins=["https://triggr4.onrender.com"])

app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# -------------------------------
# Helper Functions
# -------------------------------

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    return docx2txt.process(file_path)

def chunk_text(text: str, chunk_size: int = 500) -> list:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_embeddings(chunks: list) -> list:
    response = openai.Embedding.create(input=chunks, model="text-embedding-ada-002")
    embeddings = [data['embedding'] for data in response['data']]
    return embeddings

def call_claude_rag(context: str, question: str) -> str:
    """
    Improved RAG: Constructs a detailed prompt using the provided context and question,
    and calls Anthropic's Claude 3.5 Sonnet model.
    """
    template = (
        "You are a helpful AI assistant tasked with answering questions based on provided context. "
        "Your goal is to provide accurate and relevant answers using only the information given to you. Here's how you should proceed:\n\n"
        "First, carefully read and analyze the following context:\n\n"
        "<context>\n{{CONTEXT}}\n</context>\n\n"
        "Now, you will be presented with a question. Your task is to answer this question using only the information provided in the context above. Here's the question:\n\n"
        "<question>\n{{QUESTION}}\n</question>\n\n"
        "To answer the question effectively:\n\n"
        "1. Carefully review the context and identify information relevant to the question.\n"
        "2. Formulate a clear and concise answer based solely on the provided context.\n"
        "3. If the question cannot be fully answered using the given context, state this clearly and provide whatever partial information you can from the context.\n"
        "4. Do not include any information or assumptions that are not explicitly stated in or directly implied by the context.\n\n"
        "Format your response as follows:\n\n"
        "1. Begin with your answer to the question, enclosed in <answer> tags.\n"
        "2. After your answer, provide a brief explanation of how you arrived at your answer, enclosed in <explanation> tags. "
        "This should reference specific parts of the context that support your answer.\n\n"
        "Important reminders:\n\n"
        "- Stick strictly to the information provided in the context. Do not introduce external knowledge or make assumptions beyond what is given.\n"
        "- If the context doesn't contain enough information to answer the question fully, it's okay to say so. Provide whatever relevant information you can from the context, "
        "and explain what additional information would be needed to give a complete answer.\n"
        "- Be concise but thorough in your answer and explanation.\n"
        "- If the question asks for an opinion or judgment that isn't explicitly stated in the context, clarify that you can't provide personal opinions and instead offer relevant factual information from the context.\n\n"
        "Please proceed with answering the question based on these instructions."
    )
    prompt_text = template.replace("{{CONTEXT}}", context).replace("{{QUESTION}}", question)
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens_to_sample=8192,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text,
                    }
                ]
            }
        ]
    )
    return response.get("completion", "").strip()

# -------------------------------
# Endpoints
# -------------------------------

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category')
    title = request.form.get('title') or file.filename

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(local_path)

    # Extract text based on file type
    if filename.lower().endswith('.pdf'):
        file_type = 'pdf'
        try:
            content = extract_text_from_pdf(local_path)
        except Exception as e:
            return jsonify({"error": "Failed to extract text from PDF", "details": str(e)}), 500
    elif filename.lower().endswith(('.doc', '.docx')):
        file_type = 'doc'
        try:
            content = extract_text_from_docx(local_path)
        except Exception as e:
            return jsonify({"error": "Failed to extract text from DOC/DOCX", "details": str(e)}), 500
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Upload file to Google Cloud Storage
    gcs_filename = f"documents/{uuid.uuid4()}_{filename}"
    blob = bucket.blob(gcs_filename)
    blob.upload_from_filename(local_path)
    file_url = blob.public_url

    # Save metadata and content to Firebase Firestore
    doc_data = {
        "title": title,
        "content": content,
        "category": category,
        "file_type": file_type,
        "file_url": file_url,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    doc_ref = db.collection("knowledge_items").document()
    doc_ref.set(doc_data)
    item_id = doc_ref.id

    # Partition content and compute embeddings
    chunks = chunk_text(content, chunk_size=500)
    if chunks:
        try:
            embeddings = get_embeddings(chunks)
        except Exception as e:
            return jsonify({"error": "Failed to get embeddings", "details": str(e)}), 500

        vectors = []
        for idx, embedding in enumerate(embeddings):
            vector_id = f"{item_id}_{idx}"
            metadata = {
                "item_id": item_id,
                "chunk_index": idx,
                "category": category,
                "title": title,
                "file_type": file_type
            }
            vectors.append((vector_id, embedding, metadata))
        index.upsert(vectors=vectors)
    else:
        return jsonify({"error": "No content to process for embeddings"}), 400

    os.remove(local_path)

    return jsonify({
        "message": "File uploaded and processed",
        "item_id": item_id,
        "file_url": file_url
    })

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    if not query_text:
        return jsonify({"error": "No query provided"}), 400

    try:
        response = openai.Embedding.create(input=[query_text], model="text-embedding-ada-002")
        query_embedding = response['data'][0]['embedding']
    except Exception as e:
        return jsonify({"error": "Failed to get query embedding", "details": str(e)}), 500

    filter_query = {"category": category} if category else None
    query_response = index.query(vector=query_embedding, top_k=5, filter=filter_query)
    retrieved_chunks = query_response.get('matches', [])

    context_lines = []
    for match in retrieved_chunks:
        meta = match.get('metadata', {})
        title = meta.get('title', 'Untitled')
        chunk_index = meta.get('chunk_index', '')
        context_lines.append(f"{title} (chunk {chunk_index})")
    context = "\n".join(context_lines)

    try:
        ai_response = call_claude_rag(context, query_text)
    except Exception as e:
        return jsonify({"error": "Failed to get AI response", "details": str(e)}), 500

    return jsonify({
        "response": ai_response,
        "retrieved": retrieved_chunks
    })

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    from twilio.twiml.messaging_response import MessagingResponse
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    category = request.values.get('category', 'default')

    try:
        response = openai.Embedding.create(input=[incoming_msg], model="text-embedding-ada-002")
        query_embedding = response['data'][0]['embedding']
    except Exception as e:
        ai_response = "Error generating response."
        print("Embedding error:", e)
    else:
        query_response = index.query(vector=query_embedding, top_k=5, filter={"category": category})
        retrieved_chunks = query_response.get('matches', [])
        context_lines = []
        for match in retrieved_chunks:
            meta = match.get('metadata', {})
            title = meta.get('title', 'Untitled')
            chunk_index = meta.get('chunk_index', '')
            context_lines.append(f"{title} (chunk {chunk_index})")
        context = "\n".join(context_lines)
        try:
            ai_response = call_claude_rag(context, incoming_msg)
        except Exception as e:
            ai_response = "Error generating AI response."
            print("Claude API error:", e)

    conversation_data = {
        "from": from_number,
        "message": incoming_msg,
        "response": ai_response,
        "category": category,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("whatsapp_conversations").add(conversation_data)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(ai_response)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
