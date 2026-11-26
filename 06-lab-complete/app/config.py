"""
Config — 12-Factor: mọi cấu hình đọc từ biến môi trường.

TODO (tiêu chí 9 — Config từ environment variables):
  • Đọc các biến sau từ môi trường, có giá trị mặc định hợp lý khi chạy local:
      PORT, ENVIRONMENT, AGENT_API_KEY, REDIS_URL,
      RATE_LIMIT_PER_MINUTE, DAILY_BUDGET_USD (hoặc MONTHLY_BUDGET_USD)
  • Không hard-code secret (API key thật, mật khẩu...) trong code.
  • Liệt kê đủ các biến này trong .env.example.
"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from the process environment."""

    port: int = int(os.getenv("PORT") or "8000")
    environment: str = os.getenv("ENVIRONMENT") or "local"
    # No API key is embedded in source; deployments must provide their own.
    agent_api_key: str = os.getenv("AGENT_API_KEY") or ""
    redis_url: str = os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE") or "10")
    daily_budget_usd: float = float(os.getenv("DAILY_BUDGET_USD") or "10.0")


settings = Settings()
