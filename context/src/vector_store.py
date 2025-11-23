"""
Vector store abstraction for semantic search.
Phase 1: Simple in-memory implementation with basic text search.
Can be upgraded to pgvector for production.
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class VectorDocument:
    """Document stored in vector store"""
    project_id: str
    kind: str
    key: str
    content: str


class VectorStore:
    """
    Simple in-memory vector store with basic text search.

    For Phase 1, this provides basic functionality.
    Can be upgraded to pgvector or other vector databases later.
    """

    def __init__(self):
        self.documents: Dict[str, VectorDocument] = {}

    def upsert(self, project_id: str, kind: str, key: str, content: str) -> None:
        """
        Insert or update a document in the vector store.

        Args:
            project_id: Project ID
            kind: Document kind (e.g., "architecture_spec", "code_file")
            key: Unique key for the document
            content: Document content
        """
        doc_id = f"{project_id}:{kind}:{key}"
        self.documents[doc_id] = VectorDocument(
            project_id=project_id,
            kind=kind,
            key=key,
            content=content
        )

    def search(self, project_id: str, query: str, top_k: int = 5) -> List[str]:
        """
        Search for documents matching the query.

        For Phase 1, this is a simple keyword-based search.
        In production, this would use vector similarity.

        Args:
            project_id: Project ID to search within
            query: Search query
            top_k: Number of results to return

        Returns:
            List of document contents
        """
        query_lower = query.lower()
        results: List[Tuple[int, str]] = []

        for doc_id, doc in self.documents.items():
            if doc.project_id != project_id:
                continue

            content_lower = doc.content.lower()

            # Simple scoring based on keyword matches
            score = 0
            for word in query_lower.split():
                if word in content_lower:
                    score += content_lower.count(word)

            if score > 0:
                results.append((score, doc.content))

        # Sort by score descending and return top_k
        results.sort(reverse=True, key=lambda x: x[0])
        return [content for _, content in results[:top_k]]

    def get(self, project_id: str, kind: str, key: str) -> str:
        """
        Get a specific document by key.

        Args:
            project_id: Project ID
            kind: Document kind
            key: Document key

        Returns:
            Document content or empty string if not found
        """
        doc_id = f"{project_id}:{kind}:{key}"
        doc = self.documents.get(doc_id)
        return doc.content if doc else ""

    def list_by_kind(self, project_id: str, kind: str) -> List[str]:
        """
        List all documents of a specific kind for a project.

        Args:
            project_id: Project ID
            kind: Document kind

        Returns:
            List of document contents
        """
        results = []
        for doc_id, doc in self.documents.items():
            if doc.project_id == project_id and doc.kind == kind:
                results.append(doc.content)
        return results


# Global vector store instance
_vector_store = VectorStore()


def get_vector_store() -> VectorStore:
    """Get the global vector store instance"""
    return _vector_store
