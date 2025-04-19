# Knowledge Hub Migration to Google Cloud Platform

This document provides instructions for migrating the Knowledge Hub application from Render to Google Cloud Platform (GCP).

## Prerequisites

1. Google Cloud Platform account
2. Google Cloud SDK installed locally
3. Docker installed locally
4. Git repository with the Knowledge Hub code

## Step 1: Initial GCP Setup

### 1.1. Project Configuration

1. Access the GCP Console at [console.cloud.google.com](https://console.cloud.google.com)
2. Select your project `knowledge-hub-8eaaf` or create a new one
3. Enable the following APIs:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Secret Manager API
   - Vertex AI API
   - Cloud Storage API
   - IAM API

### 1.2. Set Up Service Accounts

1. Go to "IAM & Admin" > "Service Accounts"
2. Create a service account for Cloud Run:
   - Name: `knowledge-hub-run`
   - Roles: Cloud Run Admin, Secret Manager Secret Accessor, Storage Object Viewer, Vertex AI User

3. Create a service account for Cloud Build:
   - Name: `knowledge-hub-build`
   - Roles: Cloud Build Service Account, Cloud Run Admin, Artifact Registry Writer

### 1.3. Set Up Secret Manager

1. Go to "Security" > "Secret Manager"
2. Create secrets for each environment variable:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `PINECONE_API_KEY` (needed during transition)
   - `FIREBASE_CRED_B64`
   - `GCS_CRED_B64`
   - `WATI_API_URL`
   - `WATI_API_TOKEN`
3. Add the current values from your Render environment to each secret

## Step 2: Set Up Artifact Registry

1. Go to "Artifact Registry" > "Repositories"
2. Click "Create Repository"
   - Name: `knowledge-hub`
   - Format: Docker
   - Location: Region (e.g., `us-central1`)
3. Configure Docker authentication:
   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

## Step 3: Migrate from Pinecone to Vertex AI Vector Search

### 3.1. Cloud-Based Migration Approach

The migration from Pinecone to Vertex AI Vector Search is integrated into the Cloud Build deployment process. This approach eliminates the need to run migration scripts locally and ensures that the migration happens automatically during deployment.

The migration process works as follows:

1. A migration step is included in the `backend/cloudbuild.yaml` file
2. During deployment, Cloud Build will:
   - Install the necessary dependencies
   - Run the `cloud_migration.py` script with the appropriate parameters
   - Create the Vertex AI Vector Search index if it doesn't exist
   - Migrate all vectors from Pinecone to Vertex AI

This approach has several advantages:
- No need to install dependencies locally
- Migration runs in the cloud with proper authentication
- Can be easily disabled after the initial migration
- Automatically creates all necessary Vertex AI resources

### 3.2. Manual Migration (Alternative)

If you prefer to run the migration manually or need more control over the process, you can use the `cloud_migration.py` script directly:

1. Create a Cloud Shell session or use a GCP VM with the necessary permissions
2. Clone your repository and navigate to the backend directory
3. Install the required dependencies:
   ```bash
   pip install google-cloud-aiplatform pinecone-client
   ```
4. Run the migration script:
   ```bash
   python cloud_migration.py \
     --pinecone-api-key=your_pinecone_api_key \
     --project-id=knowledge-hub-8eaaf \
     --location=us-central1
   ```

### 3.3. Controlling Migration Behavior

After the initial migration, you may want to disable the migration step in future deployments:

1. Open `backend/cloudbuild.yaml`
2. Uncomment the `SKIP_MIGRATION=true` environment variable in the migration step
3. Alternatively, you can remove the migration step entirely once the migration is complete

## Step 4: Deploy Backend to Cloud Run

### 4.1. Manual Deployment

For the most reliable deployment experience, we recommend using Google Cloud Shell instead of local deployment. This ensures you have all the necessary tools and permissions.

**Option A: Using Google Cloud Shell (Recommended)**

1. Open Google Cloud Shell by clicking the Cloud Shell icon (>_) in the GCP Console
2. Clone your repository and navigate to the backend directory:
   ```bash
   git clone https://github.com/bdintelligence20/triggr4
   cd https://github.com/bdintelligence20/triggr4/backend
   ```

3. Build and push the Docker image:
   ```bash
   gcloud builds submit --tag us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/backend:v1
   ```
   This single command handles both building and pushing the image to Artifact Registry.

**Option B: Using Local Docker (Alternative)**

If you prefer to build locally:

1. Build the Docker image:
   ```bash
   cd backend
   docker build -t us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/backend:v1 .
   ```
   
   Note: If you're using Docker Buildx, make sure to include the dot at the end to specify the build context:
   ```bash
   cd backend
   docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/backend:v1 .
   ```

2. Push to Artifact Registry:
   ```bash
   docker push us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/backend:v1
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy knowledge-hub-backend \
     --image=us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/backend:v1 \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --memory=4Gi \
     --cpu=2 \
     --min-instances=1 \
     --max-instances=10 \
     --service-account=knowledge-hub-run@knowledge-hub-8eaaf.iam.gserviceaccount.com \
     --timeout=300 \
     --startup-cpu-boost \
     --set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,PINECONE_API_KEY=PINECONE_API_KEY:latest,FIREBASE_CRED_B64=FIREBASE_CRED_B64:latest,GCS_CRED_B64=GCS_CRED_B64:latest,WATI_API_URL=WATI_API_URL:latest,WATI_API_TOKEN=WATI_API_TOKEN:latest
   ```
   
   **Note**: The `--timeout=300` parameter increases the request timeout to 5 minutes, which is helpful for long-running operations. The `--startup-cpu-boost` parameter allocates more CPU during container startup to speed up initialization.
   
   **Important**: The `--service-account` parameter is critical as it specifies the service account that has access to the secrets in Secret Manager. Without this parameter, the deployment will fail with permission errors.

### 4.2. Continuous Deployment with Cloud Build

1. Set up a Cloud Build trigger:
   - Go to "Cloud Build" > "Triggers"
   - Click "Create Trigger"
   - Connect to your repository
   - Configure the trigger to use the `backend/cloudbuild.yaml` file

## Step 5: Deploy Frontend to Cloud Run

### 5.1. Update API Endpoint

1. Update the API endpoint in `frontend/src/services/api.ts` to point to your new backend:
   ```typescript
   // Update the base URL to your Cloud Run backend
   const API_BASE_URL = 'https://knowledge-hub-backend-[hash].run.app';
   ```

### 5.2. Manual Deployment

Similar to the backend deployment, we recommend using Google Cloud Shell for the frontend deployment.

**Option A: Using Google Cloud Shell (Recommended)**

1. Open Google Cloud Shell by clicking the Cloud Shell icon (>_) in the GCP Console
2. Clone your repository and navigate to the frontend directory:
   ```bash
   git clone [YOUR_REPO_URL]
   cd [REPO_NAME]/frontend
   ```

3. Build and push the Docker image:
   ```bash
   gcloud builds submit --tag us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/frontend:v1
   ```
   This single command handles both building and pushing the image to Artifact Registry.

**Option B: Using Local Docker (Alternative)**

If you prefer to build locally:

1. Build the Docker image:
   ```bash
   cd frontend
   docker build -t us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/frontend:v1 .
   ```
   
   Note: If you're using Docker Buildx, make sure to include the dot at the end to specify the build context:
   ```bash
   cd frontend
   docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/frontend:v1 .
   ```

2. Push to Artifact Registry:
   ```bash
   docker push us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/frontend:v1
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy knowledge-hub-frontend \
     --image=us-central1-docker.pkg.dev/knowledge-hub-8eaaf/knowledge-hub/frontend:v1 \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --memory=1Gi \
     --cpu=1 \
     --min-instances=1 \
     --max-instances=5 \
     --service-account=knowledge-hub-run@knowledge-hub-8eaaf.iam.gserviceaccount.com \
     --set-env-vars=NODE_ENV=production,BACKEND_URL=https://knowledge-hub-backend-[hash].run.app
   ```
   
   **Note**: Even though the frontend doesn't directly access secrets, using the same service account ensures consistent permissions and simplifies management.

### 5.3. Continuous Deployment with Cloud Build

1. Set up a Cloud Build trigger:
   - Go to "Cloud Build" > "Triggers"
   - Click "Create Trigger"
   - Connect to your repository
   - Configure the trigger to use the `frontend/cloudbuild.yaml` file

## Step 6: Set Up Load Balancer and Domain Mapping

### 6.1. Create Load Balancer

1. Go to "Network Services" > "Load Balancing"
2. Click "Create Load Balancer"
3. Choose "HTTP(S) Load Balancing"
4. Configure backend services for both frontend and backend
5. Configure frontend with SSL certificate
6. Set up routing rules:
   - `/api/*` to backend service
   - `/*` to frontend service

### 6.2. Configure DNS

1. Update your DNS records to point to the load balancer's IP address
2. Wait for DNS propagation

## Step 7: Monitoring and Logging Setup

1. Go to "Monitoring" > "Dashboards"
2. Create a custom dashboard for your services
3. Add metrics for:
   - Cloud Run request count
   - Cloud Run latency
   - Error rates
   - Memory usage
4. Set up alerts for critical metrics

## Step 8: Cleanup

1. Once the migration is complete and verified, you can decommission your Render services
2. Consider removing the Pinecone dependency after confirming Vertex AI Vector Search is working correctly

## Troubleshooting

### Common Issues

1. **Secret Access Issues**: Ensure the Cloud Run service account has access to all secrets
2. **Memory/CPU Limits**: If you encounter performance issues, consider increasing the memory and CPU allocation
3. **Cold Start Latency**: Use minimum instances to reduce cold start latency
4. **CORS Issues**: Ensure CORS is properly configured in the backend

### Logs and Monitoring

1. Check Cloud Run logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=knowledge-hub-backend"
   ```

2. Check Cloud Build logs:
   ```bash
   gcloud logging read "resource.type=build"
