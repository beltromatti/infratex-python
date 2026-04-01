# Infratex Python SDK

Official Python client for the [Infratex](https://infratex.io) document intelligence API. Parse PDFs, build search indexes, and generate AI-powered answers grounded in your documents.

## Installation

```bash
pip install infratex
```

## Quick start

```python
from infratex import Infratex

client = Infratex(api_key="infratex_sk_...")

# Upload and parse a PDF
doc = client.documents.upload("report.pdf")
print(doc.id, doc.status, doc.page_count)

# Index for search
index = client.documents.index(doc.id, method="vector")

# Search
results = client.searches.create(query="revenue growth", document_ids=[doc.id])
for r in results:
    print(r.score, r.content[:100])

# AI response (streamed)
for event in client.responses.create(message="Summarize the key findings", document_ids=[doc.id]):
    if event.type == "text":
        print(event.content, end="")
    elif event.type == "sources":
        print("Sources:", event.content)
```

## Authentication

Pass your API key directly or set the `INFRATEX_API_KEY` environment variable:

```python
# Explicit
client = Infratex(api_key="infratex_sk_...")

# From environment
import os
os.environ["INFRATEX_API_KEY"] = "infratex_sk_..."
client = Infratex()
```

## Resources

### Documents

```python
# Upload
doc = client.documents.upload("report.pdf")
doc = client.documents.upload("report.pdf", method="standard", collection_id="col-id")

# List
docs = client.documents.list(limit=50, offset=0, collection_id="col-id")
print(docs.total)
for d in docs:
    print(d.filename)

# Get
doc = client.documents.get("doc-id")

# Download markdown
md = client.documents.markdown("doc-id")

# Delete
client.documents.delete("doc-id")

# Index
index = client.documents.index("doc-id", method="hybrid")
```

### Searches

```python
results = client.searches.create(
    query="What is the EBITDA?",
    method="vector",
    limit=5,
    document_ids=["doc-id"],
)
for r in results:
    print(r.score, r.content[:200])
```

### Responses (streaming)

```python
for event in client.responses.create(
    message="Summarize the report",
    method="hybrid",
    limit=5,
    document_ids=["doc-id"],
):
    if event.type == "text":
        print(event.content, end="")
    elif event.type == "sources":
        print("Sources:", event.content)
    elif event.type == "done":
        print("\n--- Done ---")
```

```python
# Managed multi-turn thread with persisted scope
conv = client.conversations.create(
    title="Quarterly Analysis",
    collection_id="col-id",
)

for event in client.responses.create(
    message="How does that compare with the previous quarter?",
    method="hybrid",
    model="pro",
    conversation_id=conv.id,
):
    if event.type == "text":
        print(event.content, end="")
```

### Collections

```python
col = client.collections.create(name="Q3 Reports")
cols = client.collections.list()
col = client.collections.get("col-id")
client.collections.update("col-id", name="Q4 Reports")
client.collections.delete("col-id")
```

### Conversations

```python
conv = client.conversations.create(title="Analysis", collection_id="col-id")
convs = client.conversations.list()
conv = client.conversations.get("conv-id")  # includes messages
client.conversations.delete("conv-id")
```

### Account & Billing

```python
account = client.account.get()
print(account.tenant["email"])

billing = client.billing.get()
print(billing.balance_micros)
```

## Error handling

```python
from infratex import Infratex, InfratexError

client = Infratex(api_key="infratex_sk_...")

try:
    doc = client.documents.get("nonexistent-id")
except InfratexError as e:
    print(e.status_code)  # 404
    print(e.code)         # error code from the API
    print(str(e))         # human-readable message
```

## Configuration

```python
client = Infratex(
    api_key="infratex_sk_...",
    base_url="https://api.infratex.io",  # custom base URL
    timeout=60.0,                         # request timeout in seconds
)

# Use as a context manager
with Infratex(api_key="infratex_sk_...") as client:
    doc = client.documents.upload("report.pdf")
```

## License

MIT
