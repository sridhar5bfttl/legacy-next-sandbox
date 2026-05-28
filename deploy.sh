#!/bin/bash
# Deploy LEGACY-NEXT Sandbox to Google Cloud Run
# Usage: ./deploy.sh [GEMINI_API_KEY]

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Google Cloud project not set. Run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

GEMINI_KEY=$1
ENV_VARS=""
if [ -n "$GEMINI_KEY" ]; then
    ENV_VARS="--set-env-vars=GEMINI_API_KEY=$GEMINI_KEY"
    echo "🔑 Gemini API Key detected. Cloud deployment will use managed LLM."
else
    echo "⚠️ No Gemini API Key provided. Cloud deployment will use rule-based fallback."
fi

echo "🚀 Deploying to Google Cloud Run (Project: $PROJECT_ID)..."

# Deploy using source-based deployment (Buildpacks/Cloud Build)
gcloud run deploy legacy-next-sandbox \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1024Mi \
    --quiet \
    $ENV_VARS

echo "✅ Deployment complete!"
