# Deployment Guide

## Architecture

## Why Google Cloud Run?

- **Serverless**: scales to zero when nobody's using it (no cost when idle)
- **Auto-scaling**: handles traffic spikes automatically
- **Managed**: no servers to maintain or patch
- **Secure**: secrets stored in Secret Manager, never in code

## Deployment steps

### 1. Install Google Cloud CLI
```bash
# Download from https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Store your API key securely
```bash
# Never hardcode secrets — store them in Secret Manager
echo -n "YOUR_USDA_API_KEY" | gcloud secrets create usda-api-key --data-file=-
```

### 3. Build and push Docker image
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/meal-coach
```

### 4. Deploy to Cloud Run
```bash
gcloud run deploy meal-coach \
  --image gcr.io/YOUR_PROJECT_ID/meal-coach \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 8Gi \
  --timeout 120
```

### 5. Get your live URL
```bash
gcloud run services describe meal-coach --format='value(status.url)'
```

## Security measures

- API keys stored in Google Secret Manager (never in code or Docker image)
- HTTPS enforced by default on Cloud Run
- Container runs as non-root user
- .dockerignore excludes sensitive files from image
- Environment variables injected at runtime, not build time

## Cost estimate

- Cloud Run: ~$0 when idle (scales to zero)
- First 2 million requests/month free
- Estimated cost for 1000 users/day: ~$5-15/month