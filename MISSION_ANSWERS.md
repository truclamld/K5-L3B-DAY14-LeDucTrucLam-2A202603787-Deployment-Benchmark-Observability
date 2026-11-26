# Day 14 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key bị hardcode vào `app.py`
2. Không có config management
3. Sử dụng print để log
4. Không có health check endpoint
5. Port bị hardcode (8000)


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
1. Base image: [Your answer]
2. Working directory: [Your answer]
...

### Exercise 2.3: Image size comparison
- Develop: [X] MB
- Production: [Y] MB
- Difference: [Z]%

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