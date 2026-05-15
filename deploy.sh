#!/bin/bash
set -e

IMAGE="us-central1-docker.pkg.dev/rental-analysis-2026/rental-analysis/rental-analysis"

gcloud builds submit --tag "$IMAGE" .
gcloud run deploy rental-analysis \
  --image "$IMAGE" \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
