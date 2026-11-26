"""
Kết nối Redis dùng chung cho rate limiter và cost guard.

Yêu cầu:
  • Đọc REDIS_URL từ config
  • App vẫn phải KHỞI ĐỘNG ĐƯỢC khi Redis chưa sẵn sàng (đừng ping Redis lúc import)
  • redis_healthy() dùng cho GET /ready: Redis không kết nối được → False
"""

import redis
from redis.exceptions import RedisError

from .config import settings

# Tạo client chưa mở kết nối; Redis chỉ được truy cập khi gọi một lệnh.
r = redis.from_url(settings.redis_url, decode_responses=True)


def redis_healthy() -> bool:
    """Trả False nếu Redis chưa chạy hoặc không thể kết nối."""
    try:
        r.ping()
        return True
    except (RedisError, OSError):
        return False
