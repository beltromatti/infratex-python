"""Documents resource."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .._types import DocumentList, Document, Index, UploadedDocument

if TYPE_CHECKING:
    from .._http import HTTPClient


class Documents:
    """Interact with the ``/api/v1/documents`` endpoints."""

    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def upload(
        self,
        file_path: str,
        *,
        method: Optional[str] = None,
        pipeline: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> UploadedDocument:
        """Upload and parse a PDF document.

        Parameters
        ----------
        file_path:
            Local path to the PDF file.
        method:
            Parsing method (``"standard"``, ``"cost-efficient"``, ``"experimental"``).
        pipeline:
            Optional sub-pipeline (``"traditional"``, ``"math"``).
        collection_id:
            Optional collection to assign the document to.
        """
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/pdf")}
            data: Dict[str, Any] = {}
            if method is not None:
                data["method"] = method
            if pipeline is not None:
                data["pipeline"] = pipeline
            if collection_id is not None:
                data["collection_id"] = collection_id

            resp = self._client.request(
                "POST",
                "/api/v1/documents",
                data=data,
                files=files,
            )
        return UploadedDocument(resp)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        collection_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> DocumentList:
        """List documents.

        Parameters
        ----------
        limit:
            Maximum number of documents to return.
        offset:
            Pagination offset.
        collection_id:
            Filter by collection.
        status:
            Filter by document status.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "collection_id": collection_id,
            "status": status,
        }
        resp = self._client.request("GET", "/api/v1/documents", params=params)
        return DocumentList(resp)

    def get(self, document_id: str) -> Document:
        """Retrieve a single document by ID."""
        resp = self._client.request("GET", "/api/v1/documents/{}".format(document_id))
        return Document(resp)

    def markdown(self, document_id: str) -> str:
        """Download the parsed markdown for a document."""
        return self._client.request_text("GET", "/api/v1/documents/{}/markdown".format(document_id))

    def delete(self, document_id: str) -> None:
        """Delete a document."""
        self._client.request_no_content("DELETE", "/api/v1/documents/{}".format(document_id))

    def index(
        self,
        document_id: str,
        *,
        method: str = "vector",
    ) -> Index:
        """Create a search index for a document.

        Parameters
        ----------
        document_id:
            The document to index.
        method:
            Indexing strategy: ``"vector"`` or ``"hybrid"``.
        """
        resp = self._client.request(
            "POST",
            "/api/v1/documents/{}/indexes".format(document_id),
            json_body={"method": method},
        )
        return Index(resp)
