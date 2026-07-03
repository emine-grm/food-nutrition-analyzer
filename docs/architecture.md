# System Architecture

![Architecture](../architecture.svg)

## How it works

1. **User** uploads a food photo via the web interface
2. **Google Cloud Run** receives the request and routes it to the Docker container
3. **BLIP-2** (vision-language model) identifies what food is in the photo
4. **Core logic** checks the user's profile, restrictions, and daily targets
5. **USDA FoodData API** returns real nutritional data for the identified food
6. **Translation API** generates the report in English, French, and Arabic
7. The complete health report is returned to the user

## Security

- API keys stored in **Google Secret Manager** — never in code or Docker images
- HTTPS enforced by default on Cloud Run
- Secrets injected at runtime as environment variables

## Monitoring

- **Health monitor** pings the `/health` endpoint every 60 seconds
- **Trend analyzer** detects rising response times before they become user-visible
- **Email alert** fires immediately on 3 consecutive failures or >10% error rate
- All stats saved to `monitoring/stats.json` for historical review