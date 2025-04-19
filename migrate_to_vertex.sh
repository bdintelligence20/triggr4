#!/bin/bash

# Script to migrate Knowledge Hub from Render to Google Cloud Platform
# This script focuses on the Pinecone to Vertex AI Vector Search migration

set -e  # Exit on error

# Check for required tools
command -v gcloud >/dev/null 2>&1 || { echo "Google Cloud SDK (gcloud) is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting."; exit 1; }

# Configuration
PROJECT_ID="knowledge-hub-8eaaf"  # Replace with your actual project ID if different
REGION="us-central1"  # Replace with your preferred region
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/knowledge-hub/backend:v1"
FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/knowledge-hub/frontend:v1"

echo "=== Knowledge Hub Migration to GCP ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if user is logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "You are not logged in to gcloud. Please login first."
    gcloud auth login
fi

# Set the current project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Check for credentials file
if [ ! -f "../knowledge-hub-8eaaf-6269d789a949.json" ]; then
    echo "Error: GCP credentials file not found at ../knowledge-hub-8eaaf-6269d789a949.json"
    echo "Please ensure the credentials file is available."
    exit 1
fi

# Prompt for API keys
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
read -p "Enter your Anthropic API key: " ANTHROPIC_API_KEY
read -p "Enter your Pinecone API key: " PINECONE_API_KEY

# Export environment variables
export OPENAI_API_KEY=$OPENAI_API_KEY
export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
export PINECONE_API_KEY=$PINECONE_API_KEY
export GOOGLE_APPLICATION_CREDENTIALS="../knowledge-hub-8eaaf-6269d789a949.json"

echo "Environment variables set."
echo ""

# Step 1: Run the migration script
echo "=== Step 1: Migrating data from Pinecone to Vertex AI Vector Search ==="
echo "This may take some time depending on the amount of data..."
cd backend
python3 pinecone_to_vertex_migration.py
cd ..
echo "Migration completed."
echo ""

# Step 2: Build and push backend Docker image
echo "=== Step 2: Building and pushing backend Docker image ==="
cd backend
echo "Building backend image: $BACKEND_IMAGE"
docker build -t $BACKEND_IMAGE .
echo "Pushing backend image to Artifact Registry..."
docker push $BACKEND_IMAGE
cd ..
echo "Backend image pushed successfully."
echo ""

# Step 3: Build and push frontend Docker image
echo "=== Step 3: Building and pushing frontend Docker image ==="
cd frontend
echo "Building frontend image: $FRONTEND_IMAGE"
docker build -t $FRONTEND_IMAGE .
echo "Pushing frontend image to Artifact Registry..."
docker push $FRONTEND_IMAGE
cd ..
echo "Frontend image pushed successfully."
echo ""

# Step 4: Deploy to Cloud Run
echo "=== Step 4: Deploying to Cloud Run ==="
echo "Deploying backend service..."
gcloud run deploy knowledge-hub-backend \
  --image=$BACKEND_IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=1 \
  --max-instances=10 \
  --set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,PINECONE_API_KEY=PINECONE_API_KEY:latest,FIREBASE_CRED_B64=FIREBASE_CRED_B64:latest,GCS_CRED_B64=GCS_CRED_B64:latest,WATI_API_URL=WATI_API_URL:latest,WATI_API_TOKEN=WATI_API_TOKEN:latest

# Get the backend URL
BACKEND_URL=$(gcloud run services describe knowledge-hub-backend --region=$REGION --format="value(status.url)")
echo "Backend deployed at: $BACKEND_URL"

echo "Deploying frontend service..."
gcloud run deploy knowledge-hub-frontend \
  --image=$FRONTEND_IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=5 \
  --set-env-vars=NODE_ENV=production,BACKEND_URL=$BACKEND_URL

# Get the frontend URL
FRONTEND_URL=$(gcloud run services describe knowledge-hub-frontend --region=$REGION --format="value(status.url)")
echo "Frontend deployed at: $FRONTEND_URL"
echo ""

echo "=== Migration Complete ==="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "Next steps:"
echo "1. Set up Cloud Build triggers for continuous deployment"
echo "2. Configure a load balancer if you need a custom domain"
echo "3. Set up monitoring and alerts"
echo ""
echo "See GCP_MIGRATION.md for more details."
