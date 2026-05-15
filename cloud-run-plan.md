# Cloud Run Deployment Plan

## Steps

1. **Install `gcloud` CLI**
   - `brew install --cask google-cloud-sdk`

2. **Create a GCP project** (or use an existing one)
   - At console.cloud.google.com, create a new project and note the project ID

3. **Authenticate**
   - `gcloud auth login`
   - `gcloud config set project <PROJECT_ID>`

4. **Enable required APIs**
   - `gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com`

5. **Create an Artifact Registry repository**
   - `gcloud artifacts repositories create rental-analysis --repository-format=docker --location=us-central1`

6. **Build and push the image**
   - `gcloud builds submit --tag us-central1-docker.pkg.dev/<PROJECT_ID>/rental-analysis/rental-analysis`

7. **Deploy to Cloud Run**
   - `gcloud run deploy rental-analysis --image us-central1-docker.pkg.dev/<PROJECT_ID>/rental-analysis/rental-analysis --platform managed --region us-central1 --allow-unauthenticated --port 8501`

## Deployed

- **URL**: https://rental-analysis-229545692350.us-central1.run.app
- **Project ID**: `rental-analysis-2026`
- **Region**: `us-central1`
- **Image**: `us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis`

## Notes
- `--allow-unauthenticated` makes the app publicly accessible
- Cloud Run scales to zero when idle — no charges when no one is using it
- Replace `<PROJECT_ID>` with `rental-analysis-2026` for future commands
