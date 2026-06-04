# RUN_LOCAL.md - TeamVision AI Vision Lab 04

Nguoi thuc hien: Nguyen Thanh Tung - CNTT 17-08  
Team: TeamVision / AI Vision

## 1. Cai dependency kiem thu

```bash
npm install
```

## 2. Build Docker image

```bash
docker build -t fit4110/team-vision:lab04 .
```

## 3. Run container

```bash
docker run --rm \
  --name fit4110-team-vision-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/team-vision:lab04
```

## 4. Kiem tra health

```bash
curl http://localhost:8000/api/v1/vision/health
```

Ket qua mong doi co `status=UP`, `modelStatus=READY`, `service=team-vision`.

## 5. Chay Newman tren container

```bash
npm run test:local
```

Report sinh tai:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
```

Image tag nop bai:

```bash
docker tag fit4110/team-vision:lab04 ghcr.io/<owner>/team-vision:v0.1.0-team-vision
```
