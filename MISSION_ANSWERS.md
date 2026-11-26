# Day 14 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key bị hardcode vào `app.py`
2. Không có config management
3. Sử dụng print để log
4. Không có health check endpoint
5. Port bị hardcode (8000)


### Exercise 1.2:

```bash
python app.py

Starting agent on localhost:8000...
INFO:     Will watch for changes in these directories: ['/Users/lamha/Coding/K5-L3B-DAY14-LeDucTrucLam-2A202603787-Deployment-Benchmark-Observability/01-localhost-vs-production/develop']
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [21239] using WatchFiles
INFO:     Started server process [21241]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

```bash
curl -X POST "http://localhost:8000/ask?question=Hello"

{"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}% 
```

### Exercise 1.3: Comparison table
| Feature      | Develop             | Production                                                          | Why Important?                                                                        |
|--------------|---------------------|---------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Config/Key   | Bị hardcode         | Đọc từ file env                                                     | Tránh lộ API key cá nhân                                                              |  
| Log          | Sử dụng hàm print() | Ghi và xuất ra file JSON                                            | File JSON có thể gitignore, tránh nguy cơ lộ lọt thông tin riêng tư (bao gồm API key) |
| Health check | Không có            | Liên tục kiểm tra tình trạng agent và tự động restart nếu gặp sự cố | Giảm downtime, admin không cần phải restart thủ công nếu agent bị crash               |
| Port         | Bị hardcode (8000)  | Đọc từ file env                                                     | Linh hoạt khi chạy song song nhiều dịch vụ khác, giảm nguy cơ xung đột port           |
| Shutdown     | Hard shutdown       | Chờ hoàn thành các request hiện tại trước khi shutdown an toàn      | Tránh làm gián đoạn các request mà user đang thực hiện                                |


## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: agent-develop:latest
2. Working directory: `/app`
3. Lý do `COPY requirements.txt` trước: Nếu copy cả folder trước thì chỉ cần thay đổi trong phần code (`app.py`) sẽ khiến cho Docker phải copy và chạy lại cả folder (bao gồm việc cài đặt requirements.txt). Copy requirements.txt vào và cài trước sẽ khiến cho Docker không phải copy và cài lại module khi code thay đổi (trừ khi module thay đổi)
4. CMD là câu lệnh trong Dockerfile được chỉ định sẽ chạy đầu tiên ngay khi container được khởi động. ENTRYPOINT là file thực thi mặc định được chỉ định trong container khi chạy lệnh `docker run`. (Tham khảo: https://www.docker.com/blog/docker-best-practices-choosing-between-run-cmd-and-entrypoint/) 

### Exercise 2.2:

```bash
docker run -p 8000:8000 my-agent:develop

INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     192.168.215.1:56860 - "POST /ask?question=Hello HTTP/1.1" 200 OK
```

```bash
curl -X POST "http://localhost:8000/ask?question=Hello"

{"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}%                                          
```

### Exercise 2.3: Image size comparison
- Develop: 1.17 GB (~1198.08 MB)
- Production: 188 MB
- Difference: 84.31%

### Exercise 2.4:

Sơ đồ architecture diagram của file `02-docker/production/docker-compose.yml`:
```
                HTTP :80
[Client] ─────────────────▶ [Nginx :80]
                                  │
                                  │ chuyển tiếp request
                                  ▼
                             [Agent :8000]
                              /          \
                             /            \
                  Redis :6379          Qdrant :6333
                   [Redis]              [Qdrant]
```

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1

Nếu thiếu API key: Báo lỗi HTTP 401: "Missing API key. Include header: X-API-Key: <your-key>"
```bash
curl -i http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
  
HTTP/1.1 401 Unauthorized
date: Thu, 26 Nov 2026 07:57:13 GMT
server: uvicorn
content-length: 67
content-type: application/json

{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}%   
```

Nếu API key chính xác:

```bash
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: secret-key-123" \     
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
  
HTTP/1.1 200 OK
date: Thu, 26 Nov 2026 07:58:14 GMT
server: uvicorn
content-length: 122
content-type: application/json

{"question":"Hello","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}                                                        
```

### Exercise 4.2

```bash
curl http://localhost:8000/auth/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "demo123"}'
  
{"access_token":"[REDACTED]","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}%    
```

```bash
TOKEN="[REDACTED]"
curl -i http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
  
HTTP/1.1 200 OK
date: Thu, 26 Nov 2026 07:41:32 GMT
server: uvicorn
content-length: 192
content-type: application/json
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
referrer-policy: strict-origin-when-cross-origin

{"question":"Explain JWT","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":9,"budget_remaining_usd":1.9e-05}}%
```

### Exercise 4.3:
```bash
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
{"question":"Test 1","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":8,"budget_remaining_usd":3.7e-05}}
{"question":"Test 2","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":7,"budget_remaining_usd":5.6e-05}}
{"question":"Test 3","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":6,"budget_remaining_usd":7.7e-05}}
{"question":"Test 4","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":5,"budget_remaining_usd":9.5e-05}}
{"question":"Test 5","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":4,"budget_remaining_usd":0.000112}}
{"question":"Test 6","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":3,"budget_remaining_usd":0.00013}}
{"question":"Test 7","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":2,"budget_remaining_usd":0.000146}}
{"question":"Test 8","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":1,"budget_remaining_usd":0.000167}}
{"question":"Test 9","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":0,"budget_remaining_usd":0.000188}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":41}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":40}}
```

### Exercise 4.4: Cost guard implementation

Cost guard dùng Redis để theo dõi chi tiêu mỗi user theo tháng. Mỗi tháng có một key riêng với giới hạn **10 USD**. Trước khi gọi LLM, hàm kiểm tra chi phí dự kiến: nếu vượt giới hạn thì trả `False`, nếu không thì cộng chi phí vào Redis. Key tự hết hạn sau 32 ngày.

## Part 5: Scaling & Reliability

### Exercise 5.1–5.2: Health checks và graceful shutdown

Trong `05-scaling-reliability/develop/app.py`, `GET /health` là liveness check để báo process còn hoạt động. `GET /ready` là readiness check: trả `200` khi ứng dụng sẵn sàng và `503` khi chưa sẵn sàng hoặc đang shutdown.

Middleware đếm số request đang xử lý. Khi nhận `SIGTERM` hoặc `SIGINT`, Uvicorn bắt đầu shutdown có kiểm soát; lifespan đặt ứng dụng về trạng thái chưa sẵn sàng và chờ các request đang chạy hoàn tất, tối đa 30 giây.

**Kết quả kiểm tra:**  
- `GET /health`: 
```bash
curl http://localhost:8000/health

{"status":"ok","uptime_seconds":17.4,"version":"1.0.0","environment":"development","timestamp":"2026-11-26T09:05:12.755439+00:00","checks":{"memory":{"status":"ok","used_percent":71.7}}}%
```

- `GET /ready`: 
```bash
{"ready":true,"in_flight_requests":1}% 
```

- Graceful shutdown: 
```bash
INFO:     Started server process [36865]
INFO:     Waiting for application startup.
2026-11-26 15:49:36,505 INFO Agent starting up...
2026-11-26 15:49:36,505 INFO Loading model and checking dependencies...
2026-11-26 15:49:36,710 INFO ✅ Agent is ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Shutting down
INFO:     127.0.0.1:53383 - "POST /ask?question=hello HTTP/1.1" 200 OK
INFO:     Waiting for connections to close. (CTRL+C to force quit)
INFO:     127.0.0.1:53384 - "POST /ask?question=hello HTTP/1.1" 200 OK
INFO:     Waiting for application shutdown.
2026-11-26 15:49:56,004 INFO 🔄 Graceful shutdown initiated...
2026-11-26 15:49:56,004 INFO ✅ Shutdown complete
INFO:     Application shutdown complete.
INFO:     Finished server process [36865]
2026-11-26 15:49:56,004 INFO Received signal 15 — uvicorn will handle graceful shutdown

[1]  + done       python app.py
```

### Exercise 5.3–5.5: Stateless, Redis và load balancing

Ứng dụng production lưu session/history trong Redis thay vì RAM riêng của từng agent. Nginx phân phối request tới các agent; Redis giúp bất kỳ agent nào cũng có thể đọc tiếp lịch sử của cùng session.

**Kết quả chạy `python test_stateless.py`:**
- Tổng số request: 5
- Số instance được sử dụng: 3 (`instance-dc0820`, `instance-2f4876`, `instance-c27281`)
- Lịch sử hội thoại: đủ 10 message (5 câu hỏi và 5 câu trả lời)
- Kết quả: ✅ All requests served despite different instances; ✅ Session history preserved across all instances via Redis.

Kết quả này cho thấy các request trong cùng session đã đi qua nhiều instance nhưng history vẫn được giữ nguyên nhờ Redis. Nếu lưu state trong RAM, mỗi instance chỉ thấy dữ liệu của chính nó nên các request được chuyển sang instance khác có thể không tìm thấy history.

**Khác biệt liveness và readiness:** liveness cho biết process còn sống để platform quyết định có cần restart; readiness cho biết instance đã sẵn sàng nhận traffic hay chưa.

```bash
python test_stateless.py
============================================================
Stateless Scaling Demo
============================================================

Session ID: d39403ae-0c87-4b12-905b-cfb704e63ea0

Request 1: [instance-dc0820]
  Q: What is Docker?
  A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

Request 2: [instance-2f4876]
  Q: Why do we need containers?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 3: [instance-c27281]
  Q: What is Kubernetes?
  A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

Request 4: [instance-dc0820]
  Q: How does load balancing work?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 5: [instance-2f4876]
  Q: What is Redis used for?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

------------------------------------------------------------
Total requests: 5
Instances used: {'instance-c27281', 'instance-2f4876', 'instance-dc0820'}
✅ All requests served despite different instances!

--- Conversation History ---
Total messages: 10
  [user]: What is Docker?...
  [assistant]: Container là cách đóng gói app để chạy ở mọi nơi. Build once...
  [user]: Why do we need containers?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
  [user]: What is Kubernetes?...
  [assistant]: Đây là câu trả lời từ AI agent (mock). Trong production, đây...
  [user]: How does load balancing work?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
  [user]: What is Redis used for?...
  [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...

✅ Session history preserved across all instances via Redis!
```