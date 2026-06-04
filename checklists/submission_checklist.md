# Submission Checklist - Lab 04 TeamVision

Nguoi thuc hien: Nguyen Thanh Tung - CNTT 17-08  
Service: TeamVision / AI Vision

Nop cac artefact sau:

- [x] `Dockerfile`
- [x] `.dockerignore`
- [x] `.env.example`
- [x] `RUN_LOCAL.md`
- [x] `contracts/ai-vision.openapi.yaml`
- [x] `postman/collections/FIT4110_lab04_ai_vision_docker.postman_collection.json`
- [x] `postman/environments/FIT4110_lab04_local.postman_environment.json`
- [x] `reports/newman-lab04-local.xml` (verified against local FastAPI)
- [x] `reports/newman-lab04-local.html` (verified against local FastAPI)
- [x] Log hoac anh `GET /api/v1/vision/health`
- [ ] Docker build/run evidence tren may co Docker hoac GitHub Actions
- [ ] Image tag da push len registry: `v0.1.0-team-vision`

Lenh chinh:

```bash
docker build -t fit4110/team-vision:lab04 .
docker run --rm --name fit4110-team-vision-lab04 -p 8000:8000 --env-file .env.example fit4110/team-vision:lab04
npm run test:local
```
