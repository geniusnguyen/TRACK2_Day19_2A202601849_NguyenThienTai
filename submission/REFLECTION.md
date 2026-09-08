# Reflection — Lab 19 (Vector Store + Feature Store)

**Tên:** Nguyễn Thiện Tài  
**MSSV:** 2A202601849  
**Cohort:** AICB-P2T2 (Track 2)  
**Path đã chạy:** Lite (FastEmbed + Qdrant In-Memory + Rank-BM25 + Feast SQLite + FastAPI)  

---

## 1. Phân Tích Kết Quả Golden Set 50 Queries & Khi Nào Dùng Hybrid

### Kết quả đo lường thực tế (`make benchmark`):
- **Tổng thể Precision@10:**
  - `Keyword (BM25)`: 77.8%
  - `Semantic (Vector)`: 73.2%
  - `Hybrid (RRF, k=60)`: **78.6%** (Thắng cả hai mode thuần)

- **Chi tiết theo từng lát cắt truy vấn (Query Slices):**
  - **`exact` (n=15):** Keyword (96.7%) và Hybrid (96.7%) vượt trội Semantic (88.7%). BM25 bắt chính xác các từ khóa đặc thù như tên framework, mã model, acronyms ("Qdrant", "RRF", "P99").
  - **`paraphrase` (n=15):** Semantic và Hybrid giữ được độ tương đồng ngữ nghĩa khi câu hỏi diễn đạt lại hoàn toàn không chứa từ khóa gốc ("tự động mở rộng hạ tầng" thay vì "autoscaling").
  - **`mixed` (n=20):** **Hybrid đạt 100.0%** (so với 97.0% KW và 98.5% Semantic). Đây là kịch bản người dùng thật: kết hợp từ khóa kỹ thuật với câu hỏi tự nhiên tiếng Việt.

### Khi nào KHÔNG nên dùng Hybrid (chọn Pure BM25 hoặc Pure Vector):
1. **Dùng Pure BM25 khi:**
   - Cần latency cực thấp (<1ms thay vì ~25-50ms của embedding), hệ thống high-throughput log search, tra cứu mã SKU, mã đơn hàng, UUID, hoặc tên biến code nơi ngữ nghĩa không có giá trị và embedding dễ sinh nhiễu ảo.
2. **Dùng Pure Vector khi:**
   - Tìm kiếm đa ngữ (cross-lingual), tìm kiếm theo ý niệm trừu tượng, truy vấn bằng giọng nói/hình ảnh multimodal, hoặc tập dữ liệu có độ biến thiên từ vựng cực lớn không thể gom bằng synonym dictionary.

---

## 2. Điều Ngạc Nhiên Nhất Khi Làm Lab Này

Công thức **Reciprocal Rank Fusion (RRF)** với `k=60` `(score = sum 1 / (60 + rank))` tuy cực kỳ đơn giản về mặt toán học và hoàn toàn không cần chuẩn hóa scale điểm số (score normalization) giữa BM25 và Cosine Similarity, nhưng lại mang lại độ ổn định và triệt tiêu lỗi của cả 2 mô hình một cách ấn tượng (đưa `mixed queries` lên 100% precision).

---

## 3. Bonus Challenge

- [x] Đã làm bonus (xem thư mục `bonus/` gồm `ARCHITECTURE.md`, `agent.py`, `demo.py`)
- [ ] Pair work với: _Làm độc lập_
