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
| Agent with 16 tools; offline planner when no LLM; **provider presets** (Gemini, OpenRouter, Groq, Cerebras, Mistral, GitHub Models, NVIDIA, Ollama) with retry, throttling and failover | `agent/tools.py`, `ai/llm.py` | Same tools back the REST API, the LLM agent and MCP. `codeworld doctor` self-tests your provider |
| **Patch proposals** (Cursor/Antigravity-style edit mode, reviewed by the guardrail, never auto-applied) | `agent/patch.py` | `codeworld fix`, API, VS Code |
| **GitHub hub**: `github review-pr`, `github issue`, CI + issue-triage workflow templates | `github.py`, `.github/workflows` | works from a laptop with a token |
| **VS Code extension** (CodeLens callers/tests/risk, Ask, Impact, Review → Problems panel, Propose patch) | `vscode-extension/` | VSIX included; works in VS Code forks |
| Runtime-trace overlay for dynamic dispatch | `codeworld trace` | opt-in, executes tests |
| **MCP server** (stdio, no dependencies) | `mcp_server.py` | Give Claude Code / Cursor / Copilot the graph instead of making them grep |
| Change impact + test selection + risk score | `analysis/impact.py` | Static reverse reachability **+ git co-change** (catches coupling the graph can't see) |
| **AI-PR guardrail** | `analysis/diffreview.py` | Hallucinated imports/APIs, duplicated logic (missed reuse), layering & cycles, untested changes, risky sinks, removed-but-still-called symbols, blast radius |
| Health: cycles, dead code, hotspots, duplicates, graph-coverage, bus factor, clusters | `analysis/health.py` | `.codeworld.yml` for your own layering rules |
| Attack-surface map + secret scan | `analysis/security.py` | Endpoints → call path → dangerous sinks (triage aid, **not** a SAST replacement) |
| Onboarding guide generator | `analysis/onboarding.py` | Architecture + flow Mermaid diagrams, glossary, guided tour, good first changes, `.md` export |
| Web UI: code map (semantic zoom), chat, impact, PR guardrail, health, **3D code city**, file browser | `frontend/` | React + React Flow + three.js |
| Incremental re-indexing, safe ingestion (zip-slip, URL allow-list, size caps, no code execution) | `indexer.py`, `ingest.py` | |
| **Research suite**: auto-generated QA benchmarks, call-graph fidelity vs runtime traces, impact vs git history, seeded-fault + real-commit guardrail evaluation, figures, user-study kit; **pilot results included** | `backend/codeworld/evaluation`, `results/`, `docs/RESULTS_PILOT.md` | one command: `python -m codeworld.evaluation.suite` |

## Quick start

```bash
./scripts/setup.sh            # Windows: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
./scripts/run.sh              # open http://localhost:8000 and paste a GitHub URL
```

Full instructions, every command, optional LLM/embedding setup, MCP, Docker, CI and troubleshooting: **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)**.

## Honest status (read this before you present it)

**Verified in development** - 34 automated tests (parser, resolver, graph, retrieval, impact, health, security, onboarding, PR guardrail, git co-change, incremental re-index, URL/zip safety, REST API, MCP handshake, **LLM provider layer against a mock OpenAI/Ollama server incl. 429 retry + failover + agent loop + hallucinated-citation detection, patch proposals, API-token auth, runtime-trace overlay, class-hierarchy overrides, GitHub PR/issue flows against a mocked API + local remote, the CI workflow's CLI commands**); every UI page loads without console errors in headless Chromium; the VS Code extension loads and renders CodeLens against a stub of the VS Code API and packages to a VSIX; workflow files pass `actionlint`; indexing + Q&A + health + security ran on real repositories up to **Django (529k LOC, 49 s, ~500 MB)**; and a **pilot experiment suite** ran on 5 real repositories (`docs/RESULTS_PILOT.md`, `results/`).

**Not verified (you must test these yourself):** real Gemini / OpenRouter / Groq / Ollama calls (the sandbox could not reach them; `codeworld doctor` tests your provider in one command); CodeRankEmbed / sentence-transformers embeddings (model hosting was unreachable); Docker image (no Docker in the sandbox - GitHub `ci.yml` builds it for you); GitHub Actions on GitHub's runners and the live GitHub API (rate-limited from the sandbox); the extension inside a real VS Code / Cursor / Antigravity window; MCP with real clients; Windows and macOS (use `ci.yml` - it runs the suite on both); JS/TS beyond the small fixture. **Pilot numbers use the offline hash embedder and no LLM**, are from one machine, and were partly tuned on the same repos - confirm before publishing.

Known limitations: static call graphs miss dynamic dispatch (partly mitigated by class-hierarchy override edges and the opt-in `codeworld trace` runtime overlay); ORM-style chains (`Model.objects.filter`) stay unresolved; "dead code" flags a library's public API as low-confidence rather than hiding it; framework route prefixes are not resolved; the security view is heuristic triage, not an audit; the API token is a shared secret, not user management.

## Layout

```
backend/codeworld/     parser/ graph/ ai/ agent/ analysis/ evaluation/ api/  cli.py  mcp_server.py
backend/tests/         pytest suite + fixtures/shop_app (the demo repo)
frontend/src/          pages/ components/
docs/                  ARCHITECTURE.md  RESEARCH.md  RESULTS_PILOT.md  PROVIDERS.md  HUB_FEATURE_MAP.md  MCP.md  API.md  research/
vscode-extension/      VS Code client (+ built VSIX)
results/               pilot experiment outputs
scripts/               setup + run for bash and PowerShell
.github/workflows/     PR guardrail template for your own repositories
```

MIT licensed.
