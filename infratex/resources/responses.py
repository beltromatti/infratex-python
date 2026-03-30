"""Responses resource (streaming AI answers)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from .._types import StreamEvent

if TYPE_CHECKING:
    from .._http import HTTPClient


class Responses:
    """Interact with the ``/api/v1/responses`` endpoint."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        message: str,
        method: str = "vector",
        limit: int = 5,
        document_ids: Optional[List[str]] = None,
        collection_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Iterator[StreamEvent]:
        """Generate a streamed AI response grounded in your documents.

        Yields :class:`StreamEvent` objects with ``type`` and ``content``.
        Event types:

        - ``"sources"`` -- retrieved source chunks (list of dicts)
        - ``"text"`` -- a chunk of generated text
        - ``"done"`` -- stream complete
        - ``"error"`` -- an error occurred

        Parameters
        ----------
        message:
            The user message / question.
        method:
            ``"vector"`` or ``"hybrid"``.
        limit:
            How many source chunks to retrieve (1--20).
        document_ids:
            Restrict to these document IDs.
        collection_id:
            Restrict to this collection.
        conversation_id:
            Continue an existing conversation thread.
        """
        body: Dict[str, Any] = {
            "message": message,
            "method": method,
            "limit": limit,
        }
        if document_ids is not None:
            body["document_ids"] = document_ids
        if collection_id is not None:
            body["collection_id"] = collection_id
        if conversation_id is not None:
            body["conversation_id"] = conversation_id

        for event_data in self._client.stream_sse("POST", "/api/v1/responses", json_body=body):
            event_type = event_data.get("type", "unknown")
            content = event_data.get("content")
            yield StreamEvent(type=event_type, content=content)
