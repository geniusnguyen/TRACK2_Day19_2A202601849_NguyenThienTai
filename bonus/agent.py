"""HybridMemoryAgent — Personal AI Memory POC combining Qdrant + Feast.

Integrates episodic memories (Qdrant Vector Store) with structured user profiles
and real-time activity features (Feast Feature Store).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.embeddings import Embedder


class HybridMemoryAgent:
    """Agent that maintains episodic memories and retrieves user profile features."""

    def __init__(self, collection_name: str = "user_memories") -> None:
        self.collection_name = collection_name
        self.embedder = Embedder()
        self.client = QdrantClient(":memory:")
        self._doc_id_counter = 0

        # Initialize vector collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.embedder.dim, distance=Distance.COSINE),
        )

        # Mock / Feast Online Feature Store backing for POC
        self._user_profiles: dict[str, dict[str, Any]] = {
            "u_001": {
                "preferred_language": "vi",
                "topic_affinity": "cloud_computing, ai_infrastructure",
                "reading_speed_wpm": 280,
                "queries_last_hour": 6,
                "active_project": "Lakehouse & Vector Search Optimization",
            },
            "u_002": {
                "preferred_language": "en_vi_mixed",
                "topic_affinity": "data_engineering, kubernetes",
                "reading_speed_wpm": 320,
                "queries_last_hour": 2,
                "active_project": "Real-time Streaming Pipeline",
            }
        }

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for this user."""
        vec = next(self.embedder.embed([text])).tolist()
        point_id = self._doc_id_counter
        self._doc_id_counter += 1

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload={
                        "user_id": user_id,
                        "text": text,
                        "timestamp": "2026-09-08T18:30:00Z",
                    }
                )
            ]
        )

    def recall(self, query: str, user_id: str = "u_001", top_k: int = 3) -> str:
        """Retrieve top-K memories + user profile features → return assembled context."""
        # 1. Fetch user profile from Feature Store
        profile = self._user_profiles.get(
            user_id,
            {
                "preferred_language": "vi",
                "topic_affinity": "general",
                "reading_speed_wpm": 250,
                "queries_last_hour": 1,
                "active_project": "None",
            }
        )

        # 2. Vector search in Qdrant for episodic memory
        q_vec = next(self.embedder.embed([query])).tolist()
        hits = self.client.query_points(
            collection_name=self.collection_name,
            query=q_vec,
            limit=top_k,
        ).points

        # Filter by user_id
        user_hits = [p.payload["text"] for p in hits if p.payload.get("user_id") == user_id]

        # 3. Assemble context
        memories_str = "\n".join([f"    - {m}" for m in user_hits]) if user_hits else "    (No relevant memory found)"
        context = (
            f"[User Profile & State]\n"
            f"  User ID: {user_id}\n"
            f"  Preferred Language: {profile['preferred_language']}\n"
            f"  Topic Affinity: {profile['topic_affinity']}\n"
            f"  Reading Speed: {profile['reading_speed_wpm']} WPM\n"
            f"  Queries Last Hour: {profile['queries_last_hour']}\n"
            f"  Active Project: {profile['active_project']}\n"
            f"[Retrieved Episodic Memories for '{query}']\n"
            f"{memories_str}\n"
        )
        return context
