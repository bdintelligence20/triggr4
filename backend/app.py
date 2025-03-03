import os
import uuid
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore
firebase_cred_json = os.environ.get("FIREBASE_CRED_JSON")
if not firebase_cred_json:
    raise Exception("FIREBASE_CRED_JSON environment variable not set.")
firebase_cred_info = json.loads(firebase_cred_json)
firebase_admin.initialize_app(credentials.Certificate(firebase_cred_info))
db = firestore.client()

# Pinecone
import pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index(PINECONE_INDEX_NAME)

# Twilio
from twilio.rest import Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Cloud Storage
from google.cloud import storage
gcs_cred_json = os.environ.get("GCS_CRED_JSON")
if not gcs_cred_json:
    raise Exception("GCS_CRED_JSON environment variable not set.")
gcs_client = storage.Client.from_service_account_info(json.loads(gcs_cred_json))
GCS_BUCKET_NAME = "your-gcs-bucket-name"  # Replace with your actual bucket name
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
# Flask App and Config
# -------------------------------
app = Flask(__name__)
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

def call_claude_api(prompt: str) -> str:
    anthro_prompt = f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}"
    response = anthropic_client.completion(
        prompt=anthro_prompt,
        model="claude-v1",
        max_tokens_to_sample=300,
        stop_sequences=[anthropic.HUMAN_PROMPT]
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

    gcs_filename = f"documents/{uuid.uuid4()}_{filename}"
    blob = bucket.blob(gcs_filename)
    blob.upload_from_filename(local_path)
    file_url = blob.public_url

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
    prompt = f"Context:\n{context}\n\nUser Query: {query_text}\n\nAnswer:"

    try:
        ai_response = call_claude_api(prompt)
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
        prompt = f"Context:\n{context}\n\nUser Query: {incoming_msg}\n\nAnswer:"
        try:
            ai_response = call_claude_api(prompt)
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