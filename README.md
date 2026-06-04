# FIT4110 Lab 04 - TeamVision Docker Packaging

Student: Nguyen Thanh Tung - CNTT 17-08  
Team: TeamVision / AI Vision  
Case study: Smart Campus Operations Platform

Lab 04 packages the AI Vision API from Lab 03 into a Docker container and verifies it again with Newman.

## Service

- FastAPI package: `src/vision_app`
- Contract: `contracts/ai-vision.openapi.yaml`
- Runtime model: mock AI model (`MODEL_MODE=mock`)
- Auth: `Authorization: Bearer <AUTH_TOKEN>`
- Public health endpoint: `GET /api/v1/vision/health`

Main endpoints:

- `POST /api/v1/vision/frame-detections`
- `GET /api/v1/vision/frame-detections/{detectionId}`
- `POST /api/v1/vision/analysis-jobs`
- `GET /api/v1/vision/analysis-jobs/{jobId}`
- `GET /api/v1/vision/models/info`

## Quick Start Without Docker

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn vision_app.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/api/v1/vision/health
```

Run Newman:

```bash
npm install
npm run test:local
```

## Docker

Build image:

```bash
docker build -t fit4110/team-vision:lab04 .
```

Run container:

```bash
docker run --rm \
  --name fit4110-team-vision-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/team-vision:lab04
```

Verify container:

```bash
curl http://localhost:8000/api/v1/vision/health
npm run test:local
```

Suggested image tag for submission:

```bash
docker tag fit4110/team-vision:lab04 ghcr.io/<owner>/team-vision:v0.1.0-team-vision
```

## Newman Evidence

Reports are generated in:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
```

The collection covers functional, auth, negative, boundary/reliability, consumer-side smoke, and local-only nonfunctional checks.

## CI

GitHub Actions workflow: `.github/workflows/docker-newman.yml`

The workflow installs dependencies, lints the OpenAPI contract, builds the Docker image, starts the container, waits for `/api/v1/vision/health`, runs Newman, and uploads reports.

## Submission Artefacts

- `Dockerfile`
- `.dockerignore`
- `.env.example`
- `RUN_LOCAL.md`
- `contracts/ai-vision.openapi.yaml`
- `postman/collections/FIT4110_lab04_ai_vision_docker.postman_collection.json`
- `postman/environments/FIT4110_lab04_local.postman_environment.json`
- `reports/newman-lab04-local.xml`
- `reports/newman-lab04-local.html`
- Health/log screenshot or GitHub Actions evidence
- Image tag `v0.1.0-team-vision`
