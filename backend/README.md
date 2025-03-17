# Knowledge Hub Backend

A modular Flask application for the Knowledge Hub RAG system with LangChain integration.

## Project Structure

```
backend/
├── Dockerfile                # Docker configuration for containerization
├── app.py                    # Main application entry point
├── auth_routes.py            # Authentication routes
├── document_loaders.py       # LangChain document loaders
├── embedding_utils.py        # Embedding generation utilities
├── evaluation.py             # RAG system evaluation
├── gunicorn_config.py        # Gunicorn configuration for production
├── langchain_rag.py          # LangChain RAG implementation
├── pinecone_client.py        # Pinecone vector database client
├── rag_system.py             # Original RAG system implementation
├── render.yaml               # Render deployment configuration
├── requirements.txt          # Python dependencies
├── text_splitters.py         # LangChain text splitting utilities
├── utils.py                  # Common utility functions
├── vector_store.py           # Enhanced vector store implementation
└── routes/                   # Modularized route blueprints
    ├── __init__.py           # Package initialization
    ├── document_routes.py    # Document management routes
    ├── query_routes.py       # Query and evaluation routes
    ├── utility_routes.py     # Utility and monitoring routes
    └── whatsapp_routes.py    # WhatsApp integration routes
```

## Features

- **Enhanced Document Processing**: Support for 80+ file types
- **Advanced RAG System**: Using LangChain for improved retrieval and generation
- **Modular Architecture**: Well-organized codebase with separation of concerns
- **WhatsApp Integration**: Conversational interface via WhatsApp
- **Evaluation Framework**: Tools to measure RAG system performance
- **Multi-tenant Support**: Organization-specific knowledge bases

## Environment Variables

The application requires the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
PINECONE_API_KEY=your_pinecone_api_key
FIREBASE_CRED_B64=base64_encoded_firebase_credentials
GCS_CRED_B64=base64_encoded_gcs_credentials
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=your_twilio_whatsapp_number
```

## Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set environment variables (see above)

3. Run the development server:
   ```
   python app.py
   ```

## Running with Docker

1. Build the Docker image:
   ```
   docker build -t knowledge-hub-backend .
   ```

2. Run the container:
   ```
   docker run -p 8080:8080 --env-file .env knowledge-hub-backend
   ```

## Deployment

The application can be deployed to Render using the provided `render.yaml` configuration.

## API Endpoints

### Document Management

- `POST /upload`: Upload and process a document
- `GET /documents`: List all documents
- `DELETE /delete/<item_id>`: Delete a document

### Query

- `POST /query`: Query the knowledge base
- `POST /evaluate`: Evaluate RAG system performance

### WhatsApp

- `POST /whatsapp-webhook`: Handle incoming WhatsApp messages

### Utility

- `GET /health`: Health check endpoint
- `GET /test-pinecone`: Test Pinecone connectivity

### Authentication

- `POST /auth/register`: Register a new user
- `POST /auth/login`: Login a user
- `POST /auth/verify-otp`: Verify OTP for login
- `POST /auth/reset-password`: Reset password
