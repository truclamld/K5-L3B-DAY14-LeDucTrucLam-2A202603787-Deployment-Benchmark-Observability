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

### Exercise 2.3: Image size comparison
- Develop: 1.17 GB (~1198.08 MB)
- Production: 188 MB
- Difference: 84.31%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]