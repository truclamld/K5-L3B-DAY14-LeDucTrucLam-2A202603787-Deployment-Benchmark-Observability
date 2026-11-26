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

Cost guard cộng chi phí input/output token sau mỗi lần gọi LLM. Mỗi user có giới hạn 1 USD/ngày, toàn dịch vụ 10 USD/ngày; dùng đến 80% thì ghi cảnh báo. Trước mỗi lần gọi, guard kiểm tra giới hạn và chặn request nếu đã hết budget.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]