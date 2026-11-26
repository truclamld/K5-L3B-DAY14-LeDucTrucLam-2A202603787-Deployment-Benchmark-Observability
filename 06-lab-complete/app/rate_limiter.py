"""
Rate limiting (tiêu chí 7).

Yêu cầu:
  • Mỗi API key tối đa RATE_LIMIT_PER_MINUTE request trong 60 giây (sliding window)
  • Vượt giới hạn → HTTP 429, nên kèm header Retry-After
  • State lưu trong Redis để mọi worker / instance dùng chung và vẫn còn sau khi
    restart agent (script chấm sẽ restart agent để kiểm tra)
"""

import hashlib
import math
import secrets
import time

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from .config import settings
from .redis_client import r


# Một script Lua đảm bảo xóa, đếm và thêm request là một thao tác nguyên tử.
# Nếu làm ba lệnh Redis riêng, nhiều worker có thể cùng thấy còn quota và cùng
# nhận request, khiến giới hạn bị vượt khi traffic đến đồng thời.
_SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now_ms = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

redis.call('ZREMRANGEBYSCORE', key, '-inf', now_ms - window_ms)
local count = redis.call('ZCARD', key)
if count >= limit then
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    return {0, tonumber(oldest[2])}
end

redis.call('ZADD', key, now_ms, member)
redis.call('EXPIRE', key, math.ceil(window_ms / 1000) + 1)
return {1, 0}
"""


def check_rate_limit(key: str) -> None:
    """Cho phép tối đa N request của key trong 60 giây gần nhất."""
    now_ms = int(time.time() * 1000)
    window_ms = 60_000
    limit = settings.rate_limit_per_minute
    # Hash API key để không lưu secret trực tiếp trong tên Redis key.
    key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
    redis_key = f"agent:rate-limit:{key_hash}"
    member = f"{now_ms}:{secrets.token_hex(8)}"

    try:
        allowed, oldest_ms = r.eval(
            _SLIDING_WINDOW_SCRIPT,
            1,
            redis_key,
            now_ms,
            window_ms,
            limit,
            member,
        )
    except (RedisError, OSError) as exc:
        # Không bỏ qua giới hạn khi Redis lỗi; trả lỗi service rõ ràng.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter is unavailable",
        ) from exc

    if not allowed:
        retry_after = max(1, math.ceil((int(oldest_ms) + window_ms - now_ms) / 1000))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )
