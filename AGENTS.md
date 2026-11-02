<!-- enable-local-memory:start -->
## Automatic repository-local memory

- During **every** coding task in this repository, use the registered `enable-local-memory` skill when available and follow the memory rules below. No separate user request to remember is necessary.
- At task start: read `.agents/memory/MEMORY.md` if present; load only topic notes relevant to the current task. Treat source code as authoritative over stale notes.
- If memory is missing, initialize it. If this is an existing substantial repository with thin memory, inspect README, manifests, source, tests and relevant history; build a useful concise project/architecture/workflows memory before or during work.
- As meaningful project facts, decisions, conventions, workflows, or pitfalls emerge, update `.agents/memory/` **without being asked**. Before finishing each task, check whether any durable learning needs to be saved; do nothing for trivial/no-new-information tasks.
- Keep `.agents/memory/MEMORY.md` a short index, merge with existing notes rather than appending duplicates, fix stale entries, link evidence paths, and keep temporary handoffs current.
- Never record secrets, credentials, `.env` values, personal data, or unrelated repositories' content. Do not auto-stage/commit/push memory edits.
<!-- enable-local-memory:end -->
