# CodeWorld

**A map for any codebase.** CodeWorld parses a repository into a typed code knowledge graph, answers questions about it with *verified* citations, shows what a change will break, and reviews AI-written pull requests for the mistakes human reviewers tend to miss. It runs on a laptop CPU, needs no API key, and never executes the code it analyses.

```
Repository ──► Tree-sitter AST ──► resolved knowledge graph ──► hybrid retrieval ──► answers + citations
 (git / zip)    (Py, JS, TS)       CALLS · IMPORTS · INHERITS     BM25 + vectors      impact · tests · risk
                                   EXPOSES · TESTS · ACCESSES     + graph expansion   PR guardrail · MCP
```

## What is in the box

| Capability | Where | Notes |
|---|---|---|
| Deterministic parsing (Python, JavaScript, TypeScript) | `backend/codeworld/parser` | Symbols, imports, calls, decorators, FastAPI/Flask/Django/Express routes, side-effects |
| Knowledge graph with call resolution levels 0-3 | `graph/builder.py` | name-only → scope+imports → **+type flow (default)** → +Jedi. Each edge carries a confidence and the rule that produced it |
| Hybrid retrieval: BM25 (SQLite FTS5) + vectors + graph expansion | `ai/retrieval.py` | Zero-download hashing embedder by default; CodeRankEmbed / Ollama / OpenAI-compatible optional |
| Q&A with **citation verification** | `agent/answer.py` | Every `[path:line]` is checked against what was actually retrieved |
| Agent with 16 tools; offline planner when no LLM | `agent/tools.py` | Same tools back the REST API, the LLM agent and MCP |
| **MCP server** (stdio, no dependencies) | `mcp_server.py` | Give Claude Code / Cursor / Copilot the graph instead of making them grep |
| Change impact + test selection + risk score | `analysis/impact.py` | Static reverse reachability **+ git co-change** (catches coupling the graph can't see) |
| **AI-PR guardrail** | `analysis/diffreview.py` | Hallucinated imports/APIs, duplicated logic (missed reuse), layering & cycles, untested changes, risky sinks, removed-but-still-called symbols, blast radius |
| Health: cycles, dead code, hotspots, duplicates, graph-coverage, bus factor, clusters | `analysis/health.py` | `.codeworld.yml` for your own layering rules |
| Attack-surface map + secret scan | `analysis/security.py` | Endpoints → call path → dangerous sinks (triage aid, **not** a SAST replacement) |
| Onboarding guide generator | `analysis/onboarding.py` | Architecture + flow Mermaid diagrams, glossary, guided tour, good first changes, `.md` export |
| Web UI: code map (semantic zoom), chat, impact, PR guardrail, health, **3D code city**, file browser | `frontend/` | React + React Flow + three.js |
| Incremental re-indexing, safe ingestion (zip-slip, URL allow-list, size caps, no code execution) | `indexer.py`, `ingest.py` | |
| **Research harness**: QA retrieval metrics, impact-vs-git-history validation, call-graph fidelity, resolver ablation, dynamic-trace ground truth, user-study kit | `backend/codeworld/evaluation`, `docs/research` | See `docs/RESEARCH.md` |

## Quick start

```bash
./scripts/setup.sh            # Windows: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
./scripts/run.sh              # open http://localhost:8000 and paste a GitHub URL
```

Full instructions, every command, optional LLM/embedding setup, MCP, Docker, CI and troubleshooting: **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)**.

## Honest status (read this before you present it)

Verified in development: 21 automated tests pass (parser, resolver, graph, retrieval, impact, health, security, onboarding, PR guardrail on an AI-style diff, git co-change, incremental re-index, zip-slip and URL validation, REST API, MCP handshake, evaluation harness); every UI page loads without console errors in headless Chromium; indexing + Q&A + health + security were run on a real repository (`psf/requests`, 12k LOC indexes in about a second).

**Not verified (you must test these yourself):** the Ollama / OpenAI-compatible LLM calls and the agent loop with a *real* model (only the offline planner was exercised); the sentence-transformers / CodeRankEmbed embedding backend; the Docker image and compose file; the GitHub Actions template; MCP with real clients (only a raw JSON-RPC client was used); large repositories (>50k LOC); Windows. **No benchmark numbers for the paper have been produced** - the harness exists, the experiments are yours to run (see `docs/RESEARCH.md`).

Known limitations: static call graphs cannot see dynamic dispatch (the evaluation on the fixture shows exactly this: calls into test doubles are missed); "dead code" on a *library* flags its public API; framework route prefixes (`include_router(prefix=...)`) are not resolved; the security view is heuristic triage.

## Layout

```
backend/codeworld/     parser/ graph/ ai/ agent/ analysis/ evaluation/ api/  cli.py  mcp_server.py
backend/tests/         pytest suite + fixtures/shop_app (the demo repo)
frontend/src/          pages/ components/
docs/                  ARCHITECTURE.md  RESEARCH.md  MCP.md  API.md  research/
scripts/               setup + run for bash and PowerShell
.github/workflows/     PR guardrail template for your own repositories
```

MIT licensed.
