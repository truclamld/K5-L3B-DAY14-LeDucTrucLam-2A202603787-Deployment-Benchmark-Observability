# Benchmark & Observability Report — Day 14

> Copy file này thành `BENCHMARK_REPORT.md` trong repo của bạn và điền đầy đủ.
> Mọi con số phải lấy từ report JSON / CSV / screenshot thật, không ước lượng.

**Họ tên:** Lê Đức Trúc Lâm
**Ngày chạy:** ...
**Môi trường:** MacBook M4 Pro, OrbStack 4 CPU / 8GB RAM

---

## 1. SLO của agent

| SLI | SLO | Lý do chọn ngưỡng này |
|---|---|---|
| p95 latency `/ask` | ≤ 500 ms | Giới hạn thời gian chờ của phần lớn request; p95 vẫn phản ánh nhóm request chậm mà average có thể che khuất. |
| Error rate `/ask` | ≤ 2% | Cho phép một lượng lỗi nhỏ trong bài lab, nhưng vẫn đặt mục tiêu ít nhất 98% request thành công. |
| Accuracy trên golden dataset | ≥ 85% | Ngưỡng tối thiểu phù hợp để quality gate trong CI chặn bản có chất lượng thấp; vẫn cần kiểm tra regression so với baseline. |

---

## 2. Benchmark hiệu năng (develop, `load_test.py`)

### 2.1 Concurrency vs latency (agent v2)

| Concurrency | RPS    | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO                      |
|-------------|--------|----------|----------|----------|------------|--------------------------|
| 1           | 4.24   | 192.4    | 221.8	   | 1689.1	  | 1.00%      | 	PASS                    |
| 10          | 32.06  | 190.9    | 1677.6   | 1710.3   | 1.67%      | 	FAIL — p95              |
| 50          | 112.31 | 192.2	   | 257.3	   | 276.3	   | 1.00%      | 	PASS                    |
| 100         | 50.06  | 400.9    | 3953.3   | 4345.1   | 2.33%      | FAIL — p95 và error rate |

**Nhận xét:** RPS có tăng tuyến tính theo concurrency không? Vì sao?

RPS không tăng tuyến tính theo concurrency. Từ 1 đến 50, tăng số request chạy đồng thời giúp tận dụng thời gian agent chờ LLM, nên throughput tăng. Ở concurrency 100, RPS giảm còn 50.06 trong khi p95 tăng lên 3953.3 ms và error rate lên 2.33%. Điều này cho thấy agent hoặc môi trường chạy đã chạm giới hạn tài nguyên/xử lý; request phải chờ lâu hơn và nhiều request lỗi hơn. Kết quả load test có yếu tố ngẫu nhiên nên đỉnh ở concurrency 50 không nhất thiết là giới hạn cố định. Muốn xác định nút thắt chính xác, cần đo thêm CPU, memory và số request đang chờ.
...

### 2.2 Tail latency

| `MOCK_SLOW_RATE` | avg (ms) | p95 (ms) | p99 (ms) |
|------------------|----------|----------|----------|
| 0                | 189.9	   | 218.0    | 225.1    |
| 0.03 (mặc định)  | 225.5    | 220.3    | 1707.4   |
| 0.1              | 336.8    | 1687.7   | 1712.4   |

**Nhận xét:** Chỉ số nào nhạy nhất với request chậm? Vì sao SLO không nên đặt theo average?

p99 nhạy nhất với một lượng nhỏ request rất chậm; p95 cũng tăng khi request chậm chiếm tỷ lệ lớn hơn.

Không nên đặt SLO chỉ theo average vì nó che khuất tail latency mà một nhóm người dùng gặp phải. Dùng p95 hoặc p99 giúp đặt giới hạn trực tiếp cho độ trễ của các request chậm.
...

---

## 3. Benchmark chất lượng (develop, `eval/run_eval.py`)

| Chỉ số | Agent v1 | Agent v2 | Agent v2 (sau khi sửa KB) |
|---|---|---|---|
| Accuracy | | | |
| Avg tokens / câu | | | |
| Tổng cost (USD) | | | |
| Cost / câu đúng (USD) | | | |
| Quality gate | PASS / FAIL | PASS / FAIL | PASS / FAIL |

**Những câu v2 trả lời sai ban đầu và cách bạn sửa:**

| ID | Keyword bị thiếu | Bạn đã sửa gì |
|---|---|---|
| | | |

**Nhận xét về trade-off chất lượng / chi phí / latency giữa v1 và v2:**

...

---

## 4. Observability stack (production)

### 4.1 Screenshot

- [ ] Dashboard Grafana khi đang có tải (thấy rõ Golden Signals)
- [ ] Một trace chậm trong Jaeger (thấy span nào chiếm thời gian)
- [ ] Một trace lỗi trong Jaeger (có event `exception`)
- [ ] Trang Alerts của Prometheus với ít nhất 1 alert đang **firing**

### 4.2 Thí nghiệm "phá hệ thống"

| # | Thay đổi | Alert nào firing | Thời gian từ lúc đổi → firing | Panel nào phản ánh rõ nhất |
|---|---|---|---|---|
| A | `MOCK_ERROR_RATE=0.2` | | | |
| B | `MOCK_SLOW_RATE=0.3` | | | |
| C | `LLM_MODEL=mock-llm-large` | | | |
| D | `docker pause` 1 instance | | | |
| E | `AGENT_VERSION=v1` | | | |

**Thí nghiệm E không làm alert nào firing. Bạn sẽ phát hiện loại sự cố này trong production bằng cách nào?**

...

### 4.3 Debug bằng trace

Chọn 1 trace chậm nhất bạn tìm được:

- `trace_id`: ...
- Tổng thời gian: ... ms
- Span chiếm nhiều thời gian nhất: ... (... ms, ...%)
- Dòng log tương ứng (grep theo `trace_id`):

```json

```

---

## 5. Benchmark scaling (production, Locust headless, 100 users, 2 phút)

| Số instance | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---|---|---|---|---|---|
| 1 | | | | | |
| 3 | | | | | |

**Giải thích kết quả:** Scale có cải thiện p95 không? Nút thắt nằm ở đâu?

...

---

## 6. Kết luận

- 3 điều bạn học được về benchmark & observability:
  1. ...
  2. ...
  3. ...
- Nếu đưa agent này lên production thật, bạn sẽ thêm metric / alert nào nữa?

...
