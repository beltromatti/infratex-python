"""Conversations resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .._types import Conversation

if TYPE_CHECKING:
    from .._http import HTTPClient


class Conversations:
    """Interact with the ``/api/v1/conversations`` endpoints."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def create(self, *, title: str = "New Chat") -> Conversation:
        """Create a new conversation thread."""
        resp = self._client.request(
            "POST", "/api/v1/conversations", json_body={"title": title}
        )
        return Conversation(resp)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Conversation]:
        """List conversations.

        Parameters
        ----------
        limit:
            Maximum number of conversations to return (1--100).
        offset:
            Pagination offset.
        """
        params = {"limit": limit, "offset": offset}
        resp = self._client.request("GET", "/api/v1/conversations", params=params)
        return [Conversation(c) for c in resp]

    def get(self, conversation_id: str) -> Conversation:
        """Retrieve a conversation and its messages."""
        resp = self._client.request("GET", "/api/v1/conversations/{}".format(conversation_id))
        return Conversation(resp)

    def delete(self, conversation_id: str) -> None:
        """Delete a conversation."""
        self._client.request_no_content("DELETE", "/api/v1/conversations/{}".format(conversation_id))
