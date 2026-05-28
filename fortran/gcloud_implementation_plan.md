# Serverless Cloud Migration & Optional LLM Architecture

To deploy this application to Google Cloud while keeping costs extremely low (Approach B), we will host the Docker container on **Google Cloud Run** and route the interactive agent chat directly to the managed **Gemini API** using the new `google-genai` SDK, completely eliminating the need for expensive 24/7 GPU instances.

## Proposed Changes

### Configuration & Infrastructure
#### [MODIFY] [Dockerfile](file:///Volumes/superfast/LinkedIn/Classic_Code/Dockerfile)
- Add `google-genai` and `requests` to the `pip install` command to enable communication with Google Cloud's managed Vertex AI / Gemini endpoints.

#### [NEW] [deploy.sh](file:///Volumes/superfast/LinkedIn/Classic_Code/deploy.sh)
- Create a deployment script that contains the `gcloud run deploy` command. This will automatically build the container and deploy it to a serverless Cloud Run instance that scales to zero (incurring $0 when not in use).

### Backend LLM Routing
#### [MODIFY] [app.py](file:///Volumes/superfast/LinkedIn/Classic_Code/src/app.py)
We will rewrite the LLM pipeline in `app.py` to follow this cascade:
1. **Managed Cloud LLM (Primary for Cloud)**: Check for `GEMINI_API_KEY`. If present, use `gemini-2.5-flash` for high-speed, cheap code analysis.
2. **Local Foundry (Primary for Local dev)**: If no API key is found, attempt to connect to the local `foundry.local` container as it does today.
3. **Rule-Based Fallback (Offline mode)**: If neither the API key nor the local daemon is available, gracefully fall back to the rule-based expert system without throwing any HTTP 500 errors to the frontend.

Update the `/api/llm-status` endpoint to report "Gemini Cloud API" as the source when the API key is detected, so the UI dashboard updates accordingly.

## User Review Required

> [!IMPORTANT]  
> Cloud Run deployments require the Google Cloud CLI (`gcloud`) to be installed and authenticated on your local machine. I will provide the deployment script, but you will need to execute it and provide a Gemini API key if you want the chatbot to function in the cloud. Is this acceptable?

## Verification Plan

### Automated Tests
1. Rebuild the Docker image locally.
2. Run the container **without** an API key and verify that the LLM health dot turns yellow and it uses the rule-based fallback.
3. Run the container **with** `GEMINI_API_KEY=xxx` and verify that the LLM health dot turns green and reports "Gemini Cloud API".

### Manual Verification
Execute `sh deploy.sh` and verify the provided Cloud Run URL loads the Fortran sandbox correctly in the cloud.
