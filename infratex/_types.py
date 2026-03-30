"""Typed response objects returned by the Infratex SDK."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class _Base:
    """Lightweight base that populates attributes from a dict."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        name = type(self).__name__
        fields = ", ".join(
            "{}={!r}".format(k, v)
            for k, v in self._data.items()
            if not k.startswith("_")
        )
        return "{}({})".format(name, fields)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
class Document(_Base):
    id: str
    filename: str
    status: str
    method: str
    pipeline: Optional[str]
    page_count: Optional[int]
    processing_time_ms: Optional[int]
    error_message: Optional[str]
    markdown_size_bytes: Optional[int]
    chunk_count: Optional[int]
    index_method: Optional[str]
    collection_id: Optional[str]
    markdown: Optional[str]
    upload_time: Optional[str]
    extraction_pages: Optional[List[Dict[str, Any]]]


class UploadedDocument(_Base):
    id: str
    status: str
    method: str
    filename: str
    pipeline: Optional[str]
    page_count: Optional[int]
    markdown: Optional[str]
    extraction_ms: int
    collection_id: Optional[str]
    extraction_pages: Optional[List[Dict[str, Any]]]


class DocumentList(_Base):
    documents: List[Document]
    total: int

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        self.documents = [Document(d) for d in data.get("documents", [])]

    def __iter__(self):  # type: ignore
        return iter(self.documents)

    def __len__(self) -> int:
        return len(self.documents)


# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------
class Index(_Base):
    document_id: str
    filename: str
    method: str
    status: str
    node_count: int
    chunk_count: int
    has_ast: bool
    has_description: bool
    processing_ms: int


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
class SearchResult(_Base):
    document_id: str
    document_name: Optional[str]
    score: float
    content: str
    title: str
    summary: str
    node_id: Optional[str]
    chunk_index: Optional[int]
    metadata: Optional[Dict[str, Any]]
    source: str


class SearchResponse(_Base):
    method: str
    query: str
    results: List[SearchResult]

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        self.results = [SearchResult(r) for r in data.get("results", [])]

    def __iter__(self):  # type: ignore
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


# ---------------------------------------------------------------------------
# Responses (SSE streaming)
# ---------------------------------------------------------------------------
class StreamEvent:
    """A single event from the SSE response stream."""

    __slots__ = ("type", "content")

    def __init__(self, type: str, content: Any) -> None:
        self.type = type
        self.content = content

    def __repr__(self) -> str:
        return "StreamEvent(type={!r}, content={!r})".format(self.type, self.content)


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------
class Collection(_Base):
    id: str
    name: str
    created_at: str


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------
class Conversation(_Base):
    id: str
    title: str
    created_at: str
    updated_at: Optional[str]
    messages: Optional[List[Dict[str, Any]]]


# ---------------------------------------------------------------------------
# Account & Billing
# ---------------------------------------------------------------------------
class Account(_Base):
    tenant: Dict[str, Any]


class BillingSummary(_Base):
    balance_micros: int
    recent_transactions: List[Dict[str, Any]]
    recent_credit_transactions: List[Dict[str, Any]]
    recent_usage: List[Dict[str, Any]]
    spend_by_service: List[Dict[str, Any]]
    daily_spend: List[Dict[str, Any]]
    totals: Dict[str, Any]
