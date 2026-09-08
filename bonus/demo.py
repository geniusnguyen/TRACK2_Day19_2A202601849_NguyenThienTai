"""Demo script for HybridMemoryAgent (5 queries demonstration).

Demonstrates episodic memory retrieval combined with structured user profile context.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bonus.agent import HybridMemoryAgent


def main() -> int:
    print("=== HybridMemoryAgent Demo (Day 19 Bonus Challenge) ===\n")
    agent = HybridMemoryAgent()

    # Seed episodic memories for u_001
    print("1. Ingesting user episodic memories...")
    memories = [
        "Đã đọc bài báo về Kubernetes autoscaling với KEDA và horizontal pod autoscaler.",
        "Ghi chú nghiên cứu: Qdrant vector index hỗ trợ HNSW và filtered payload search rất tốt cho tiếng Việt.",
        "Kiến trúc Cloud Security: Quản lý IAM role-based access control và mTLS giữa các microservices.",
        "Báo cáo chi phí: Tiết kiệm 40% chi phí S3 nhờ Delta Lake OPTIMIZE Z-ORDER và định kỳ VACUUM.",
        "Tài liệu kỹ thuật: Triển khai Feast feature store với SQLite online store cho low latency lookup.",
    ]
    for m in memories:
        agent.remember(m, user_id="u_001")
    print(f"  Seeded {len(memories)} memories for user 'u_001'.\n")

    # 5 Demonstration Queries
    queries = [
        ("Query 1 (Vector memory hit)", "Tôi đã đọc gì về Kubernetes?"),
        ("Query 2 (Profile-guided recommendation)", "Recommend đọc gì tiếp theo?"),
        ("Query 3 (Recent activity & state)", "Tôi đang quan tâm gì gần đây?"),
        ("Query 4 (Paraphrase semantic match)", "Tài liệu về tự động mở rộng hạ tầng?"),
        ("Query 5 (Mixed episodic + profile)", "Cho tôi summary cloud security."),
    ]

    print("2. Executing 5 Demonstration Queries:\n" + "=" * 60)
    for title, q in queries:
        print(f"\n>>> [{title}]: '{q}'")
        context = agent.recall(q, user_id="u_001", top_k=2)
        print(context)
        print("-" * 60)

    print("\nAll 5 demonstration queries executed successfully with exit code 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
