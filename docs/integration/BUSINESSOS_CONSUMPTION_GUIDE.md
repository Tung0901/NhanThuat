# BusinessOS Consumption Guide

**Document ID:** `DOC-INT-002`

## Consuming NhanThuat

BusinessOS acts as the operational orchestrator. When querying NhanThuat for knowledge, you must use the adapter provided in `nhan_thuat.public.v1.adapter`.

### 1. Initialization

```python
from nhan_thuat.public.v1.adapter import KnowledgeEngineAdapterV1

provider = KnowledgeEngineAdapterV1()
```

### 2. Querying Knowledge

```python
from nhan_thuat.public.v1 import KnowledgeQuery

query = KnowledgeQuery(domain_slug="human-nature", limit=10)
result = provider.query_knowledge(query)

print(f"Total Matches: {result.total_matches}")
for unit in result.units:
    print(unit.title)
```

### 3. Handling Capabilities

Check if a capability is implemented before invoking it:

```python
capabilities = provider.list_capabilities()
for cap in capabilities:
    if cap.status == "IMPLEMENTED":
        # Safe to use
        pass
```
