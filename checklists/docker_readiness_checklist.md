# Docker Readiness Checklist - TeamVision

## Dockerfile

- [x] Base image hop ly: `python:3.11-slim`.
- [x] Co `WORKDIR`.
- [x] Copy dependency truoc source de tan dung cache.
- [x] Co `EXPOSE 8000`.
- [x] Co `CMD` chay `uvicorn vision_app.main:app`.
- [x] Co `HEALTHCHECK` goi `/api/v1/vision/health`.
- [x] Co user non-root `appuser`.
- [x] Khong chua secret that.

## Runtime

- [ ] Container TeamVision build/run duoc tren may co Docker.
- [x] Port map `8000:8000`.
- [x] `/api/v1/vision/health` tra `200` khi chay local FastAPI.
- [x] Cau hinh qua `.env.example`.
- [x] Model runtime dung mock model (`MODEL_MODE=mock`).

## Testing

- [ ] Newman collection TeamVision chay tren container.
- [x] Newman report sinh trong `reports/`.
- [x] Functional test pass.
- [x] Auth test pass tren container.
- [x] Negative test pass tren container.
- [x] Boundary/reliability test pass tren container.

## Evidence

- [x] Co Newman XML/HTML report tu local FastAPI verification.
- [x] Co health endpoint de chup anh/log.
- [x] Image tag de nop: `v0.1.0-team-vision`.
- [ ] Can chay Docker Desktop/CI de lay log `docker build`, `docker run`, va Newman tren container.
