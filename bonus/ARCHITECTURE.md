# Personal AI Assistant Memory System — Architecture Design Brief

**Author:** Nguyễn Thiện Tài (MSSV: 2A202601849)  
**Track:** AICB-P2T2 — Day 19 Bonus Challenge  
**Target:** Hybrid Memory Architecture for Personal AI Assistant in Vietnamese Context  

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph UserInteraction["1. User Interaction Layer"]
        User([Vietnamese User]) -->|Prompts & Notes / Reading Stream| Router[AI Assistant Gateway / Memory Router]
    end

    subgraph MemoryIngestion["2. Ingestion & Dual-Store Processing"]
        Router -->|Episodic Text| Chunker[Semantic Vietnamese Chunker<br/>*256 tokens + 32 overlap*]
        Chunker -->|Embedding fastembed / bge-m3| VecDB[(Qdrant Vector Store<br/>*Episodic Memories with user_id payload*)]
        
        Router -->|User Activity Events| EventStream[Activity Logger / Kafka Stream]
        EventStream -->|Real-time Feast Push / Materialize| FeastStore[(Feast Online Store<br/>*User Profile + Recent Activity*)]
    end

    subgraph RetrievalAugmentation["3. Hybrid Context Assembly"]
        User -->|Query: 'Tóm tắt bảo mật đám mây'| HybridRetriever[Hybrid Memory Agent]
        HybridRetriever -->|1. Online Features Lookup| FeastStore
        HybridRetriever -->|2. Filtered Hybrid Search (BM25 + Dense Qdrant)| VecDB
        FeastStore -->|Topic affinity, WPM, Last 1h Queries| ContextBuilder[Context Assembler & Sanitizer]
        VecDB -->|Top-K Episodic Memory Chunks| ContextBuilder
    end

    subgraph Generation["4. LLM Generation"]
        ContextBuilder -->|Personalized & Grounded Prompt| LLM[LLM Engine]
        LLM -->|Customized Vietnamese Response| User
    end
```

---

## 2. Three Key Architectural Decisions & Explicit Tradeoffs

### Decision 1: Chunking Strategy for Episodic Memory (256 Tokens with 32-Token Overlap vs Full Conversations)
- **Decision:** Chia nhỏ ghi chú và đoạn hội thoại thành các chunk 256 tokens với 32 tokens overlap, phân cách dựa trên dấu câu tiếng Việt (`.`, `?`, `!`, `\n`).
- **Tradeoff Analysis:**
  - *Xem xét:* Lưu nguyên toàn bộ phiên hội thoại (full thread 2000-4000 tokens) vào Vector DB để giữ toàn cảnh ngữ cảnh.
  - *Lý do loại bỏ & Chọn lựa:* Full conversation khiến vector embedding bị pha loãng (vector drift), giảm mạnh similarity score khi user chỉ hỏi về một ý cụ thể. Chunk 256 tokens tối ưu hóa retrieval density, giảm 75% chi phí lưu trữ vector và cho phép ghép nhiều mẩu ký ức độc lập vào context window của LLM mà không bị tràn token.

### Decision 2: Dual-Store Strategy (Feast Tabular Feature Store vs Vector Store for User Profile)
- **Decision:** Tách bạch rõ rệt: **Qdrant** lưu Episodic Memory không cấu trúc (suy nghĩ, tài liệu đã đọc, ghi chú), còn **Feast** lưu Tabular Profile có cấu trúc (`reading_speed_wpm`, `preferred_language`, `topic_affinity`, `queries_last_hour`).
- **Tradeoff Analysis:**
  - *Xem xét:* Encode cả user profile thành embedding vector rồi lưu chung trong Vector DB.
  - *Lý do chọn Feast:* Profile người dùng cần cập nhật tức thời (point update) với độ trễ P99 < 5ms. Nếu nhúng profile vào vector, mỗi lần user đọc thêm 1 bài báo, hệ thống phải re-embed toàn bộ profile history. Feast cho phép cập nhật từng feature riêng biệt (`queries_last_hour`) qua Push API và hỗ trợ Point-in-time (PIT) join cho training model cá nhân hóa sau này.

### Decision 3: Multi-Tier Freshness Strategy (Sub-second vs 5-Minute vs Daily)
- **Decision:** Áp dụng chính sách độ tươi (freshness) 3 tầng:
  1. **Sub-second (Immediate):** Ghi nhận episodic memories vào in-memory/WAL của Qdrant ngay lập tức để query kế tiếp có thể nhớ ngay.
  2. **5-Minute Streaming:** Cập nhật sliding window features (`queries_last_hour`, `recent_topics`) vào Feast Online Store qua Push Source.
  3. **Daily Batch:** Tính toán lại các aggregate feature dài hạn (`primary_interest_cluster`, `average_wpm`) vào Feast Offline Store (Parquet/Delta) rồi materialize sang Online Store lúc 2:00 AM.

---

## 3. Vietnamese-Context Considerations

1. **Xử lý Mã Trộn (Code-Switching vi/en):**
   - Người dùng công nghệ Việt Nam thường xuyên trộn từ tiếng Anh ("check log", "deploy k8s", "tự động scale pod"). Sử dụng bộ tokenizer FastEmbed / BGE hỗ trợ đa ngữ kết hợp BM25 trên từ vựng tiếng Việt giúp không bị mất mát thông tin khi từ ghép tiếng Anh đi liền câu hỏi tiếng Việt.
2. **Tối ưu hóa Tìm kiếm Tương đối (Phonetic & Diacritic Robustness):**
   - Bộ lọc tiền xử lý chuẩn hóa dấu tiếng Việt (Unicode NFC) và loại bỏ lỗi gõ telex giúp các câu hỏi không dấu hoặc gõ sai telex vẫn match chính xác với tài liệu gốc trong Vector DB.

---

## 4. Honest Limitations of this POC

- Chưa triển khai phân quyền đa người dùng nâng cao (Row-Level Security / Tenant Isolation hoàn chỉnh trên disk).
- Chưa tích hợp cơ chế tự động nén ký ức cũ (Hierarchical Memory Summarization / Sleep-time consolidation).
- Mã hóa dữ liệu tĩnh (Encryption-at-Rest) cho bộ nhớ nhạy cảm của người dùng cần được hoàn thiện ở phiên bản Production.
