# Research guide: turning CodeWorld into a paper

The harness (`codeworld eval ...`) and the instrumentation are built; **the experiments and numbers are yours to produce.** Nothing in this repository claims a benchmark result.

## 1. Positioning (be honest about novelty)

Graph-RAG over code is already an active area. Related work to read and cite (verify each reference yourself - these were found via web search, not read in full):

- **CodexGraph** - LLM agents querying a code graph database (NAACL 2025, arXiv 2408.03910).
- **CodeRAG** - retrieval for repository-level code generation (EMNLP 2025).
- **Reliable Graph-RAG for Codebases: AST-derived vs LLM-extracted knowledge graphs** (arXiv 2601.08773): AST graphs build fast and cover all files; vector-only retrieval struggles on architecture questions. Closest to your design rationale.
- **Beyond Code Snippets: repository-level QA** (arXiv 2603.26567): StackRepoQA (Java), graph-based RAG vs file-based RAG.
- **Code-Graph-RAG**, **codebase-memory-mcp** (open-source tools; the latter has an accompanying paper, arXiv 2603.27277 - verify) - direct competitors/prior art for graph + MCP.
- Also: RepoGraph, LARGER (arXiv 2605.16352), CodeRankEmbed model card (Nomic) for the embedder.

So "we built Graph-RAG for code" is **not** a contribution. Defensible contributions, in order of strength:

| # | Contribution | Why it is novel enough | Experiment |
|---|---|---|---|
| C1 | **Impact analysis validated against git history**, comparing static graph vs co-change vs hybrid | Most tools ship impact analysis without ground truth | `eval impact` |
| C2 | **Resolver ablation**: how call-resolution fidelity (name-only → scope → type-flow → Jedi) changes retrieval, QA and impact quality | Prior work treats the graph as given | `eval resolver-ablation` |
| C3 | **Small / CPU-only models**: does the graph compensate for weak models more than for strong ones? | Most papers use frontier LLMs | `eval qa` with several models |
| C4 | **AI-PR guardrail**: detection of hallucinated imports/APIs, duplicate logic and architectural drift in agent-written changes | Fits the AI-code-quality debate; little graph-based work | seeded-fault + real-PR study |
| C5 | **Human study**: onboarding-task time/accuracy with vs without CodeWorld | Gives the UI a research contribution | `docs/research/USER_STUDY.md` |

Pick **C1 + C2 (+ C3)** for a solid empirical paper; add C4 or C5 if time allows. Suggested title: *"How much does call-graph fidelity matter? Impact analysis and repository QA with small models on CPU."*

## 2. Research questions and hypotheses

- **RQ1 (C3)** Does graph-augmented hybrid retrieval beat BM25 / vector / hybrid on repository QA, and is the gain larger for small local models? *H1: graph > hybrid on symbol-recall and answer correctness; the gap widens as model size shrinks.*
- **RQ2 (C2)** How does resolver level (0-3) affect call-graph precision/recall, retrieval recall, and impact accuracy? *H2: level 2 improves recall over level 1 with little precision loss; level 0 hurts precision strongly; Jedi adds a small further gain.* (A pilot on the bundled fixture already shows level 1 → 2 raising recall of executed call edges from 0.56 to 0.75; the misses are calls through duck-typed test doubles. Treat it as an illustration, not a result.)
- **RQ3 (C1)** Which predictor best identifies the other files changed in a commit: static graph, co-change, hybrid, or churn baseline? *H3: hybrid > either alone; a non-trivial share of truly co-changed files is invisible to the static graph.*
- **RQ4 (C4)** What fraction of seeded AI-style defects (invented imports/members, duplicate helpers, layer violations) does the guardrail catch, and at what false-positive rate on real PRs?
- **RQ5 (C5)** Does CodeWorld reduce time-to-correct-answer on onboarding tasks?

## 3. Data you need to build

1. **Repositories (8-15)** across sizes; include *recent or obscure* ones to limit training-data contamination (famous repos are memorised by LLMs - a major threat). Mix libraries and applications; Python plus a few JS/TS. Clone **with history** (`CODEWORLD_CLONE_DEPTH=2000`).
2. **QA dataset (100-200 questions)** in the format below. Write questions in 5 categories (locate, flow, callers, impact, explain), have 2 people write gold files/symbols independently and reconcile (report inter-annotator agreement).
   ```json
   {"id":"q1","type":"flow","question":"...","gold_files":["a/b.py"],"gold_symbols":["Class.method"],"gold_keywords":["token"]}
   ```
   For comparability also run on StackRepoQA (Java) once you add a Java parser, or restrict to its Python-like subsets.
3. **Call-graph ground truth**: (a) dynamic traces of the test suite via `dynamic_trace.py` (an *under*-approximation: report recall, and precision only on executed callers), plus (b) a **manually labelled sample** (e.g., 300 call sites over 5 repos) for exact precision.
4. **Seeded faults for RQ4**: script 100+ mutations on real PRs/commits: rename an imported name, import a non-existent package, copy-paste a helper under a new name, add an import across a layer boundary, delete a still-used function. Plus 50-100 *unmodified* real PRs to measure false positives.

## 4. Experiments - exact commands

```bash
# RQ1: retrieval + answer quality; run once per model (set CODEWORLD_LLM_* between runs; "none" = offline planner)
codeworld eval qa REPO --dataset qa_repoA.json --modes bm25,vector,hybrid,graph,agentic --k 5 --out qa_repoA_<model>.json
# RQ2: resolver ablation (re-indexes at levels 0..3, restores the default afterwards)
codeworld eval resolver-ablation REPO --truth truth.json --dataset qa_repoA.json --out ablation_repoA.json
# RQ3: impact vs git history (time-split 70/30, leave-one-out per file)
codeworld eval impact REPO --commits 400 --out impact_repoA.json
# call-graph fidelity only
codeworld eval callgraph REPO --truth truth.json
```
Metrics produced: `file_recall@k, file_mrr, sym_recall@k, sym_mrr, citation_precision, gold_file_cited, keyword_coverage, tokens, latency_ms` (+ optional LLM-judge 1-5 if you extend `--judge`); impact: `precision@5/10, recall@5/10, MAP@20`, and the Venn split *only-static / only-cochange / both / neither*; call graph: `precision, recall, F1, precision_executed_callers`.

**Statistics**: bootstrap 95% CIs over questions/commits (≥1,000 resamples); paired Wilcoxon signed-rank for system comparisons per repo, Holm correction across comparisons; report effect sizes. Fix random seeds; log model name, quantisation, temperature (0-0.1), commit SHAs of every repository.

**Ablations worth adding**: AST-aware chunking vs fixed windows; with/without identifier splitting in BM25; embedder `hash` vs CodeRankEmbed; graph expansion depth 1 vs 2; confidence threshold on edges (0 / 0.5 / 0.8).

## 5. Threats to validity (write these down)

- *Impact eval uses the HEAD graph for historical commits* (stated limitation); mitigate by restricting to recent commits.
- *Co-change in large refactors/renames is noise*; the miner skips commits with >40 files and uses `--no-renames`.
- *Dynamic ground truth is incomplete*; use the manual sample for precision.
- *LLM judge bias and non-determinism*; use human-checked subsample, temperature ≈ 0, multiple runs.
- *Training-data contamination* for popular repos; include post-cutoff or private-ish repos.
- *Python-centric heuristics* (type flow); JS/TS support is shallower.
- *Author = tool builder*: pre-register hypotheses and metrics before running experiments.

## 6. Paper outline (IMRaD; maps onto a Research-Methodology report)

1. **Abstract** (problem, method, 2-3 quantified findings, availability)
2. **Introduction** - the AI-code comprehension gap; contributions list (C1-C3 …)
3. **Background & related work** - table comparing CodexGraph, CodeRAG, Code-Graph-RAG, codebase-memory-mcp, CodeWorld on: languages, graph construction, resolution fidelity reporting, impact validation, CPU-only, MCP
4. **Approach** - graph schema, resolver levels, hybrid retrieval + expansion, citation verification, impact/co-change, guardrail
5. **Experimental setup** - repos (table with SHA, LOC, language), datasets, baselines, metrics, models, hardware (CPU model, RAM)
6. **Results** - RQ1…RQ4 tables + figures (resolver level vs F1; impact P@k bars; Venn of truth coverage)
7. **Discussion & threats**
8. **Conclusion & future work** (more languages, type-aware JS/TS, SCIP indexers, incremental PR graphs, learned re-ranker)
Artifact: this repository + dataset + scripts (aim for a reproducibility badge).

## 7. Suggested timeline (12 weeks)

W1-2 build repo list + QA set + manual call labels · W3 baselines run (offline) · W4-5 LLM runs (2-3 model sizes) · W6 resolver ablation · W7 impact eval + seeded faults · W8 stats + figures · W9 human study (pilot then run) · W10-11 writing · W12 revision, artifact packaging.

## 8. Where each piece lives
`backend/codeworld/evaluation/{qa_eval,impact_eval,callgraph_eval,dynamic_trace,runner}.py` · sample dataset `evaluation/datasets/shop_app_qa.json` (toy; replace it) · user-study kit `docs/research/`.
