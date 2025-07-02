"""
Document search service for semantic search using pgvector.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import text, func
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from app.db.models.document import Document, DocumentMetadata, DocumentEmbedding
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentSearchService:
    """Semantic search on `documents` + `document_embeddings` (pgvector)."""

    def __init__(self, db: Session, embedding_service: EmbeddingService) -> None:
        self.db = db
        self.embedding_service = embedding_service

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────
    # async def semantic_search(
    #     self,
    #     query: str,
    #     *,
    #     limit: int = 5,
    #     similarity_threshold: float = 0.70,
    #     category_filter: str | None = None,
    #     language: str | None = "en",          
    #     user_id: int | None = None,
    # ) -> List[Dict]:
    #     """
    #     RAG-style semantic search.

    #     Returns a list of dicts with keys:
    #     ─ id, title, content, source, category, created_at, updated_at,
    #       similarity, distance, metadata
    #     """
    #     # 1) embed the query ----------------------------------------------------
    #     query_vec = await self.embedding_service.generate_embedding(query)
    #     if query_vec is None:
    #         logger.error("Failed to embed query '%s'", query[:80])
    #         return []

    #     # 2) build SQL ----------------------------------------------------------
    #     where_clauses = [
    #         "1 - (e.embedding <=> :q_vec) >= :threshold"
    #     ]
    #     bind: dict[str, object] = {
    #         "q_vec": query_vec,
    #         "threshold": similarity_threshold,
    #         "limit": limit,
    #     }

    #     if category_filter:
    #         where_clauses.append("d.category = :category")
    #         bind["category"] = category_filter
    #     if language:
    #         where_clauses.append("(d.language IS NULL OR d.language = :lang)")  # language column is optional
    #         bind["lang"] = language

    #     sql = text(
    #         f"""
    #         SELECT
    #             d.id,
    #             d.title,
    #             d.content,
    #             d.source,
    #             d.category,
    #             d.created_at,
    #             d.updated_at,
    #             (e.embedding <=> :q_vec)            AS distance,
    #             1 - (e.embedding <=> :q_vec)        AS similarity
    #         FROM   document_embeddings e
    #         JOIN   documents            d ON d.id = e.document_id
    #         WHERE  {' AND '.join(where_clauses)}
    #         ORDER  BY e.embedding <=> :q_vec
    #         LIMIT  :limit
    #         """
    #     )

    #     # 3) run query & shape results -----------------------------------------
    #     rows = self.db.execute(sql, bind).fetchall()

    #     docs: list[dict] = []
    #     for r in rows:
    #         doc = {
    #             "id":         r.id,
    #             "title":      r.title,
    #             "content":    r.content,
    #             "source":     r.source,
    #             "category":   r.category,
    #             "created_at": r.created_at,
    #             "updated_at": r.updated_at,
    #             "similarity": float(r.similarity),
    #             "distance":   float(r.distance),
    #             "metadata":   self._get_metadata(r.id),
    #         }
    #         docs.append(doc)

    #     logger.info("semantic_search[%s] → %d hits", query[:60] + "…", len(docs))
    #     return docs
    
    # ────────────────────────────────────────────────────────────────
# Public API – implémentation stable
# ────────────────────────────────────────────────────────────────
    async def semantic_search(
        self,
        query: str,
        *,
        limit: int = 5,
        similarity_threshold: float = 0.70,
        category_filter: str | None = None,
        language: str | None = "en",
        user_id: int | None = None,
    ) -> List[Dict]:

        embed = await self.embedding_service.generate_embedding(query)
        if not embed:
            return []

        query_vec = list(embed)
        sim_expr  = 1 - DocumentEmbedding.embedding.cosine_distance(query_vec)

        # 1️⃣  Construire la requête SANS limit()
        q = (
            self.db.query(
                Document.id,
                Document.title,
                Document.content,
                Document.source,
                Document.category,
                Document.created_at,
                Document.updated_at,
                sim_expr.label("similarity"),
            )
            .join(DocumentEmbedding, DocumentEmbedding.document_id == Document.id)
            .filter(sim_expr >= similarity_threshold)
            .order_by(DocumentEmbedding.embedding.cosine_distance(query_vec))
        )

        # 2️⃣  Filtres optionnels AVANT le .limit()
        if category_filter:
            q = q.filter(Document.category == category_filter)
        if language:
            q = q.filter((Document.language.is_(None)) | (Document.language == language))

        # 3️⃣  LIMIT en dernier
        rows = q.limit(limit).all()

        return [
            {
                "id":         r.id,
                "title":      r.title,
                "content":    r.content,
                "source":     r.source,
                "category":   r.category,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "similarity": float(r.similarity),
                "metadata":   self._get_metadata(r.id),
            }
            for r in rows
        ]
    
    # async def semantic_search(
    #     self,
    #     query: str,
    #     limit: int,
    #     similarity_threshold: float,
    #     user_id: int,
    #     lang: str = "en",
    # ) -> List[Dict]:
    #     # 1) Get your list[float] embedding:
    #     raw_emb = await self.embedding_service.generate_embedding(query)

    #     # 2) Wrap it in pgvector.Vector
    #     query_vec = Vector(raw_emb)

    #     rows = (
    #         self.db.query(
    #             DocumentEmbedding.id,
    #             DocumentEmbedding.document_id,  
    #             (1 - (DocumentEmbedding.embedding.cosine_distance(query_vec))).label("distance"),
    #             (1 - (DocumentEmbedding.embedding.cosine_distance(query_vec))).label("similarity"),
    #             Document.title, Document.content, Document.source, Document.category
    #     )

        
    #     # # # 3) SQLAlchemy + pgvector <=> operator:
    #     # # # rows = (
    #     # # #     self.db.query(
    #     # # #         DocumentEmbedding,
    #     # # #         (1 - (DocumentEmbedding.embedding.cosine_distance(query_vec))).label("distance"),
    #     # # #         (1 - (DocumentEmbedding.embedding.cosine_distance(query_vec))).label("similarity"),
    #     # # #         Document.title, Document.content, Document.source, Document.category
    #     # # #     )
    #         .join(Document, Document.id == DocumentEmbedding.document_id)
    #         .filter(
    #             (1 - DocumentEmbedding.embedding.cosine_distance(query_vec)) >= similarity_threshold,
    #             # Document.language == lang
    #         )
    #         .order_by(DocumentEmbedding.embedding.cosine_distance(query_vec))
    #         .limit(limit)
    #         .all()
    #     )

    #     # Pack into dicts for your ChatbotService
    #     results = []
    #     for doc_id, dist, sim, title, content, source, category in rows:
    #         results.append({
    #             "document_id": doc_id, 
    #             #"document_id": emb.document_id,
    #             "title": title,
    #             "content": content,
    #             "source": source,
    #             "category": category,
    #             "distance": dist,
    #             "similarity": sim,
    #         })
    #     return results

    async def search_by_category(
        self, category: str, *, limit: int = 10, language: str | None = "en"
    ) -> List[Dict]:
        """Lightweight keyword search (no embeddings)."""
        q = self.db.query(Document).filter(Document.category == category)
        if language:
            q = q.filter((Document.language.is_(None)) | (Document.language == language))
        docs = q.limit(limit).all()
        return [
            {
                "id": d.id,
                "title": d.title,
                "content": d.content,
                "source": d.source,
                "category": d.category,
                "created_at": d.created_at,
                "updated_at": d.updated_at,
                "metadata": self._get_metadata(d.id),
            }
            for d in docs
        ]

    async def get_similar_documents(
        self,
        document_id: int,
        *,
        limit: int = 5,
        similarity_threshold: float = 0.80,
    ) -> List[Dict]:
        """k-NN search around a reference document."""
        vec = self.db.execute(
            text("SELECT embedding FROM document_embeddings WHERE document_id = :id"),
            {"id": document_id},
        ).scalar()

        if vec is None:
            logger.warning("Document %s has no embedding – aborting similarity search", document_id)
            return []

        sql = text(
            """
            SELECT
                d.id,
                d.title,
                d.content,
                d.source,
                d.category,
                d.created_at,
                d.updated_at,
                1 - (e.embedding <=> :v) AS similarity
            FROM   document_embeddings e
            JOIN   documents            d ON d.id = e.document_id
            WHERE  d.id <> :doc_id
              AND  1 - (e.embedding <=> :v) >= :thr
            ORDER  BY e.embedding <=> :v
            LIMIT  :lim
            """
        )
        rows = self.db.execute(
            sql,
            {"v": vec, "doc_id": document_id, "thr": similarity_threshold, "lim": limit},
        ).fetchall()

        return [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "source": r.source,
                "category": r.category,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "similarity": float(r.similarity),
                "metadata": self._get_metadata(r.id),
            }
            for r in rows
        ]

    # ────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────
    def _get_metadata(self, doc_id: int) -> Dict[str, str]:
        try:
            rows = (
                self.db.query(DocumentMetadata)
                .filter(DocumentMetadata.document_id == doc_id)
                .all()
            )
            return {r.key: r.value for r in rows}
        except Exception as exc:  # pragma: no cover
            logger.error("Metadata fetch failed for document %s: %s", doc_id, exc)
            return {}
    
    async def get_document_statistics(self) -> Dict:
        """Get statistics about the document collection."""
        try:
            total_docs = self.db.query(func.count(Document.id)).scalar()
            category_counts = self.db.query(
                Document.category,
                func.count(Document.id)
            ).group_by(Document.category).all()
            docs_with_embeddings = self.db.query(func.count(Document.id)).filter(
                Document.embedding.isnot(None)
            ).scalar()
            return {
                "total_documents": total_docs,
                "documents_with_embeddings": docs_with_embeddings,
                "categories": {c: cnt for c, cnt in category_counts},
                "embedding_coverage": docs_with_embeddings / total_docs if total_docs else 0
            }
        except Exception as e:
            logger.error(f"Error getting document statistics: {str(e)}")
            return {}
    
    async def search_with_filters(
        self,
        query: str,
        filters: Dict,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Perform semantic search with additional filters."""
        try:
            query_embedding = await self.embedding_service.generate_embedding(query)
            if not query_embedding:
                return []
            
            # --- NEW: join document_embeddings ---
            sql_query = """
                SELECT DISTINCT
                    d.id,
                    d.title,
                    d.content,
                    d.source,
                    d.category,
                    d.created_at,
                    d.updated_at,
                    1 - (e.embedding <=> %s::vector) as similarity
                FROM   document_embeddings e
                JOIN   documents            d ON d.id = e.document_id
            """
            where_clauses = ["1 - (e.embedding <=> %s::vector) >= %s"]
            params = [query_embedding, similarity_threshold]
            
            # category filter
            if filters.get("category"):
                where_clauses.append("d.category = %s")
                params.append(filters["category"])
            # source filter
            if filters.get("source"):
                where_clauses.append("d.source LIKE %s")
                params.append(f"%{filters['source']}%")
            # metadata filters
            if filters.get("metadata"):
                sql_query += " LEFT JOIN document_metadata dm ON d.id = dm.document_id"
                for k, v in filters["metadata"].items():
                    where_clauses.append("(dm.key = %s AND dm.value = %s)")
                    params.extend([k, v])
            # date filters
            if filters.get("date_from"):
                where_clauses.append("d.created_at >= %s")
                params.append(filters["date_from"])
            if filters.get("date_to"):
                where_clauses.append("d.created_at <= %s")
                params.append(filters["date_to"])
            
            sql_query += " WHERE " + " AND ".join(where_clauses)
            sql_query += " ORDER BY e.embedding <=> %s::vector LIMIT %s"
            params.extend([query_embedding, limit])

            rows = self.db.execute(text(sql_query), params).fetchall()
            
            documents = []
            for row in rows:
                doc_dict = {
                    "id": row.id,
                    "title": row.title,
                    "content": row.content,
                    "source": row.source,
                    "category": row.category,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "similarity": float(row.similarity)
                }
                metadata = self._get_document_metadata(row.id)
                doc_dict["metadata"] = metadata
                documents.append(doc_dict)
            return documents
        except Exception as e:
            logger.error(f"Error in filtered search: {str(e)}")
            return []

