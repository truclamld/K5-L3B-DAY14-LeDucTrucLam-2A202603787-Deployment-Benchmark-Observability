"""Production AI Agent — Part 6 Final Project."""
import json
import logging
import math
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from utils.mock_llm import ask as llm_ask

from .auth import verify_api_key
from .cost_guard import check_budget, record_cost
from .redis_client import redis_healthy
from .rate_limiter import check_rate_limit


class JsonFormatter(logging.Formatter):
    """Format application log records as one valid JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "lvl": record.levelname,
        }
        message = record.getMessage()
        try:
            details = json.loads(message)
        except (TypeError, json.JSONDecodeError):
            details = None
        if isinstance(details, dict):
            payload.update(details)
        else:
            payload["event"] = message
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("production_agent")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Let Uvicorn own SIGTERM handling and drain in-flight requests on shutdown."""
    logger.info("application_start")
    try:
        yield
    finally:
        # Uvicorn waits for active requests before invoking this shutdown hook.
        logger.info("application_shutdown")


app = FastAPI(title="Production AI Agent", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str | None = None


@app.middleware("http")
async def log_requests(request, call_next):
    """Log each request as structured JSON, including handled error responses."""
    started = time.perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "ms": round((time.perf_counter() - started) * 1000, 2),
                },
                ensure_ascii=False,
            )
        )


@app.get("/health")
def health():
    """Liveness: process is alive; deliberately independent of Redis."""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness: Redis is reachable, so stateful requests can be served."""
    if not redis_healthy():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is not ready",
        )
    return {"status": "ready"}


@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    # Kiểm tra lần lượt trước khi gọi mô hình để request không xác thực hoặc
    # vượt quota/budget không tiêu tốn thêm tài nguyên.
    check_rate_limit(api_key)
    check_budget()

    answer = llm_ask(body.question)
    # Mock LLM không cung cấp token usage; ước lượng xấp xỉ 1 token / 4 ký tự.
    input_tokens = max(1, math.ceil(len(body.question) / 4))
    output_tokens = max(1, math.ceil(len(answer) / 4))
    request_cost = record_cost(input_tokens, output_tokens)

    logger.info(
        json.dumps(
            {
                "event": "llm_usage",
                "input_tokens_estimated": input_tokens,
                "output_tokens_estimated": output_tokens,
                "cost_usd": request_cost,
                "user_id": body.user_id,
            },
            ensure_ascii=False,
        )
    )
    return {"question": body.question, "answer": answer}
