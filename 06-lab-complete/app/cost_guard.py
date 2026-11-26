"""
Cost guard (tiêu chí 8).

Yêu cầu:
  • Cộng dồn chi phí LLM (tính theo token) vào Redis
  • Tổng chi phí vượt DAILY_BUDGET_USD (hoặc MONTHLY_BUDGET_USD) → HTTP 402
"""

from datetime import datetime, time as day_time, timedelta, timezone

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from .config import settings
from .redis_client import r


# Giá USD / 1K tokens (tham khảo gpt-4o-mini)
PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006


def _daily_cost_key(now: datetime | None = None) -> tuple[str, int]:
    """Trả về Redis key theo ngày UTC và số giây còn lại đến ngày mới."""
    current = now or datetime.now(timezone.utc)
    next_day = datetime.combine(
        current.date() + timedelta(days=1), day_time.min, tzinfo=timezone.utc
    )
    ttl = max(1, int((next_day - current).total_seconds()))
    return f"agent:cost:{current.date().isoformat()}", ttl


def check_budget() -> None:
    """Gọi TRƯỚC khi gọi LLM. Hết budget → raise HTTPException(status_code=402)."""
    redis_key, _ = _daily_cost_key()
    try:
        current_cost = float(r.get(redis_key) or 0.0)
    except (RedisError, OSError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cost guard is unavailable",
        ) from exc

    if current_cost >= settings.daily_budget_usd:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Daily usage budget exceeded",
        )


def record_cost(input_tokens: int, output_tokens: int) -> float:
    """Gọi SAU khi gọi LLM. Cộng chi phí của request vào tổng, trả về chi phí request."""
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts must be non-negative")

    request_cost = (
        input_tokens * PRICE_INPUT_PER_1K + output_tokens * PRICE_OUTPUT_PER_1K
    ) / 1000
    redis_key, ttl = _daily_cost_key()
    try:
        # incrbyfloat cộng dồn an toàn ở Redis; SET TTL lần đầu để bộ đếm tự hết
        # hạn lúc sang ngày UTC mới.
        pipe = r.pipeline()
        pipe.incrbyfloat(redis_key, request_cost)
        pipe.expire(redis_key, ttl)
        pipe.execute()
    except (RedisError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cost guard is unavailable",
        ) from exc

    return request_cost
