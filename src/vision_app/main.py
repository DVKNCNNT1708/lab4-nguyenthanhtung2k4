import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl


SERVICE_NAME = os.getenv("SERVICE_NAME", "team-vision")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.4.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")
MODEL_MODE = os.getenv("MODEL_MODE", "mock")


app = FastAPI(
    title="FIT4110 Lab 04 - TeamVision AI Vision Service",
    version=SERVICE_VERSION,
    description="Dockerized mock AI Vision API for Smart Campus TeamVision.",
)


class AnalysisType(str, Enum):
    PERSON_DETECTION = "PERSON_DETECTION"
    ATTENDANCE_RECOGNITION = "ATTENDANCE_RECOGNITION"
    SLEEPING_DETECTION = "SLEEPING_DETECTION"
    FIGHTING_DETECTION = "FIGHTING_DETECTION"
    FALL_DETECTION = "FALL_DETECTION"
    CROWD_DETECTION = "CROWD_DETECTION"
    PHONE_USAGE_DETECTION = "PHONE_USAGE_DETECTION"
    INTRUSION_DETECTION = "INTRUSION_DETECTION"


class MediaType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    FRAME = "FRAME"


class ProcessingStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int = Field(..., ge=400, le=599)
    detail: str
    instance: Optional[str] = None
    traceId: Optional[str] = None


class FrameDetectionRequest(BaseModel):
    requestId: str
    cameraId: str
    roomId: Optional[str] = None
    frameUrl: HttpUrl
    capturedAt: datetime
    analysisTypes: List[AnalysisType] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class AnalysisJobRequest(BaseModel):
    requestId: str
    sourceService: str
    sourceId: Optional[str] = None
    mediaType: MediaType
    mediaUrl: HttpUrl
    roomId: Optional[str] = None
    cameraId: Optional[str] = None
    requestedAt: datetime
    analysisTypes: List[AnalysisType] = Field(..., min_length=1)


FRAME_RESULTS: Dict[str, Dict[str, Any]] = {}
JOB_RESULTS: Dict[str, Dict[str, Any]] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def problem(
    status_code: int,
    title: str,
    detail: str,
    instance: Optional[str] = None,
    problem_type: str = "about:blank",
) -> Dict[str, Any]:
    return {
        "type": problem_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "traceId": f"trace-{uuid4()}",
    }


def detect_risk(analysis_types: List[AnalysisType]) -> RiskLevel:
    if AnalysisType.FIGHTING_DETECTION in analysis_types:
        return RiskLevel.HIGH
    if AnalysisType.CROWD_DETECTION in analysis_types or AnalysisType.SLEEPING_DETECTION in analysis_types:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def detection_object(analysis_types: List[AnalysisType]) -> Dict[str, Any]:
    label = "person"
    class_id = "person"
    if AnalysisType.FIGHTING_DETECTION in analysis_types:
        label = "fighting"
        class_id = "fighting"
    elif AnalysisType.SLEEPING_DETECTION in analysis_types:
        label = "student_sleeping"
        class_id = "student_sleeping"
    elif AnalysisType.CROWD_DETECTION in analysis_types:
        label = "crowd"
        class_id = "crowd"

    return {
        "objectId": f"obj-{uuid4().hex[:8]}",
        "classId": class_id,
        "label": label,
        "confidence": 0.91,
        "riskLevel": detect_risk(analysis_types).value,
        "trackingId": f"track-{uuid4().hex[:8]}",
        "boundingBox": {"x": 120, "y": 80, "width": 220, "height": 300},
        "attributes": {"modelMode": MODEL_MODE},
    }


def build_detection_result(
    *,
    id_field: str,
    id_value: str,
    request_id: str,
    camera_id: Optional[str],
    room_id: Optional[str],
    media_type: Optional[MediaType],
    media_url: Optional[str],
    analysis_types: List[AnalysisType],
) -> Dict[str, Any]:
    risk = detect_risk(analysis_types)
    item = detection_object(analysis_types)
    summary = {
        "totalObjects": 1,
        "highestRiskLevel": risk.value,
        "eventType": analysis_types[0].value,
    }
    result = {
        id_field: id_value,
        "requestId": request_id,
        "status": ProcessingStatus.COMPLETED.value,
        "processedAt": now_iso(),
        "detections": [item],
        "summary": summary,
    }
    if camera_id:
        result["cameraId"] = camera_id
    if room_id:
        result["roomId"] = room_id
    if media_type:
        result["mediaType"] = media_type.value
    if media_url:
        result["mediaUrl"] = media_url
    return result


def verify_bearer_token(authorization: Optional[str] = Header(default=None)) -> None:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=problem(
                status.HTTP_401_UNAUTHORIZED,
                "Unauthorized",
                "Missing Authorization header",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )
    if authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=problem(
                status.HTTP_401_UNAUTHORIZED,
                "Unauthorized",
                "Invalid bearer token",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    content = exc.detail if isinstance(exc.detail, dict) else problem(
        exc.status_code,
        status.HTTP_STATUS_CODES.get(exc.status_code, "HTTP Error"),
        str(exc.detail),
        instance=str(request.url.path),
    )
    content.setdefault("instance", str(request.url.path))
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        media_type="application/problem+json",
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(part) for part in first.get("loc", []))
    message = first.get("msg", "Request validation error")
    detail = f"{location}: {message}" if location else message
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation error",
            detail,
            instance=str(request.url.path),
            problem_type="https://smart-campus.local/problems/validation-error",
        ),
        media_type="application/problem+json",
    )


@app.get("/api/v1/vision/health")
def health() -> Dict[str, Any]:
    return {
        "status": "UP",
        "modelStatus": "READY",
        "timestamp": now_iso(),
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "owner": "Nguyen Thanh Tung - CNTT 17-08",
    }


@app.post(
    "/api/v1/vision/frame-detections",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token)],
)
def create_frame_detection(payload: FrameDetectionRequest) -> Dict[str, Any]:
    detection_id = str(uuid4())
    FRAME_RESULTS[detection_id] = build_detection_result(
        id_field="detectionId",
        id_value=detection_id,
        request_id=payload.requestId,
        camera_id=payload.cameraId,
        room_id=payload.roomId,
        media_type=None,
        media_url=None,
        analysis_types=payload.analysisTypes,
    )
    return {
        "detectionId": detection_id,
        "requestId": payload.requestId,
        "status": ProcessingStatus.PROCESSING.value,
        "message": "Frame analysis request accepted",
    }


@app.get("/api/v1/vision/frame-detections/{detectionId}", dependencies=[Depends(verify_bearer_token)])
def get_frame_detection(detectionId: UUID) -> Dict[str, Any]:
    key = str(detectionId)
    if key not in FRAME_RESULTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=problem(
                status.HTTP_404_NOT_FOUND,
                "Not Found",
                "Frame detection result not found",
                instance=f"/api/v1/vision/frame-detections/{key}",
                problem_type="https://smart-campus.local/problems/not-found",
            ),
        )
    return FRAME_RESULTS[key]


@app.post(
    "/api/v1/vision/analysis-jobs",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token)],
)
def create_analysis_job(payload: AnalysisJobRequest) -> Dict[str, Any]:
    job_id = str(uuid4())
    JOB_RESULTS[job_id] = build_detection_result(
        id_field="jobId",
        id_value=job_id,
        request_id=payload.requestId,
        camera_id=payload.cameraId,
        room_id=payload.roomId,
        media_type=payload.mediaType,
        media_url=str(payload.mediaUrl),
        analysis_types=payload.analysisTypes,
    )
    return {
        "jobId": job_id,
        "requestId": payload.requestId,
        "status": ProcessingStatus.PROCESSING.value,
        "message": "Analysis job accepted",
    }


@app.get("/api/v1/vision/analysis-jobs/{jobId}", dependencies=[Depends(verify_bearer_token)])
def get_analysis_job(jobId: UUID) -> Dict[str, Any]:
    key = str(jobId)
    if key not in JOB_RESULTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=problem(
                status.HTTP_404_NOT_FOUND,
                "Not Found",
                "Analysis job not found",
                instance=f"/api/v1/vision/analysis-jobs/{key}",
                problem_type="https://smart-campus.local/problems/not-found",
            ),
        )
    return JOB_RESULTS[key]


@app.get("/api/v1/vision/models/info", dependencies=[Depends(verify_bearer_token)])
def get_model_info() -> Dict[str, Any]:
    return {
        "modelName": "SmartCampus-MockVision",
        "version": SERVICE_VERSION,
        "status": "READY",
        "framework": "FastAPI mock model",
        "supportedAnalysisTypes": [item.value for item in AnalysisType],
        "updatedAt": now_iso(),
        "description": "Mock AI model for FIT4110 Lab 04 Docker packaging.",
    }
