# Deployment Information

## Public URL
https://03787-agent-production.up.railway.app/

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://03787-agent-production.up.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://03787-agent-production.up.railway.app/ask \
  -H "X-API-Key: YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT: 8000
- REDIS_URL: URL nội bộ của Redis trên Railway
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)