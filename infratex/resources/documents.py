"""Documents resource."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .._http import InfratexError
from .._types import DocumentList, Document, Index, UploadedDocument

if TYPE_CHECKING:
    from .._http import HTTPClient


class Documents:
    """Interact with the ``/api/v1/documents`` endpoints."""

    _poll_interval_seconds = 1.0

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
        created = Document(resp)
        return self._wait_for_uploaded_document(created.id)

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

    def _wait_for_uploaded_document(self, document_id: str) -> UploadedDocument:
        deadline = time.monotonic() + self._client.timeout_seconds

        while True:
            document = self.get(document_id)
            if document.status in {"done", "parsed", "indexed"}:
                return UploadedDocument(
                    {
                        "id": document.id,
                        "status": document.status,
                        "method": document.method,
                        "filename": document.filename,
                        "pipeline": document.pipeline,
                        "page_count": document.page_count,
                        "markdown": self.markdown(document_id),
                        "extraction_ms": document.processing_time_ms or 0,
                        "collection_id": document.collection_id,
                        "extraction_pages": document.extraction_pages,
                    }
                )
            if document.status == "error":
                raise InfratexError(
                    document.error_message or "Document processing failed",
                    status_code=409,
                    code="document_processing_failed",
                )
            if time.monotonic() >= deadline:
                raise InfratexError(
                    "Document processing timed out",
                    status_code=504,
                    code="upload_timeout",
                )
            time.sleep(self._poll_interval_seconds)

    def delete(self, document_id: str) -> None:
        """Delete a document."""
        self._client.request_no_content("DELETE", "/api/v1/documents/{}".format(document_id))

    def index(
        self,
        document_id: str,
        *,
        method: str = "vector",
        wait: bool = True,
    ) -> Index:
        """Create a search index for a document.

        Parameters
        ----------
        document_id:
            The document to index.
        method:
            Indexing strategy: ``"vector"`` or ``"hybrid"``.
        wait:
            When ``True`` (default), poll until the index reaches ``indexed``.
        """
        resp = self._client.request(
            "POST",
            "/api/v1/documents/{}/indexes".format(document_id),
            json_body={"method": method},
        )
        created = Index(resp)
        if not wait:
            return created
        return self.get_index(document_id, method, wait=True)

    def list_indexes(self, document_id: str) -> List[Index]:
        """List index resources for a document."""
        resp = self._client.request("GET", "/api/v1/documents/{}/indexes".format(document_id))
        return [Index(index) for index in resp]

    def get_index(
        self,
        document_id: str,
        method: str,
        *,
        wait: bool = False,
    ) -> Index:
        """Retrieve a single index resource for a document."""
        if not wait:
            resp = self._client.request(
                "GET",
                "/api/v1/documents/{}/indexes/{}".format(document_id, method),
            )
            return Index(resp)
        return self._wait_for_document_index(document_id, method)

    def _wait_for_document_index(self, document_id: str, method: str) -> Index:
        deadline = time.monotonic() + self._client.timeout_seconds

        while True:
            index = self.get_index(document_id, method, wait=False)
            if index.status == "indexed":
                return index
            if index.status == "error":
                raise InfratexError(
                    index.error_message or "Indexing failed",
                    status_code=409,
                    code="index_failed",
                )
            if time.monotonic() >= deadline:
                raise InfratexError(
                    "Indexing timed out",
                    status_code=504,
                    code="index_timeout",
                )
            time.sleep(self._poll_interval_seconds)
