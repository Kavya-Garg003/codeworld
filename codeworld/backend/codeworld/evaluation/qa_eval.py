"""Retrieval + answer quality evaluation on a QA dataset.

Dataset format (JSON list):
  {"id": "q1", "type": "locate|flow|callers|impact|explain", "question": "...",
   "gold_files": ["app/services/auth_service.py"], "gold_symbols": ["AuthService.login"], "gold_keywords": ["token"]}
Retrieval modes: bm25, vector, hybrid, graph.  `agentic` runs the full ask() pipeline (LLM agent when configured, offline planner otherwise).
"""
from __future__ import annotations
import json
import statistics
import time

from ..agent.answer import ask
from ..ai.intent import classify

RETRIEVAL_MODES = ("bm25", "vector", "hybrid", "graph")


def _recall(gold: list[str], got: list[str], k: int, suffix: bool = False) -> float | None:
    if not gold:
        return None
    top = got[:k]
    hit = sum(1 for g in gold if any((x == g or (suffix and (x.endswith("." + g) or x.endswith("/" + g) or x == g))) for x in top))
    return hit / len(gold)


def _mrr(gold: list[str], got: list[str], suffix: bool = False) -> float | None:
    if not gold:
        return None
    for i, x in enumerate(got, 1):
        if any(x == g or (suffix and (x.endswith("." + g) or x.endswith("/" + g))) for g in gold):
            return 1.0 / i
    return 0.0


def _dedupe(seq):
    return list(dict.fromkeys(seq))


def evaluate(ctx, dataset: list[dict], modes: list[str], k: int = 5, judge: bool = False) -> dict:
    g = ctx.graph
    results: dict[str, list[dict]] = {m: [] for m in modes}
    for q in dataset:
        for mode in modes:
            t0 = time.time()
            row = {"id": q["id"], "type": q.get("type", "")}
            if mode in RETRIEVAL_MODES:
                hits = ctx.retriever.search(q["question"], mode, max(k, 10), classify(q["question"]))
                files = _dedupe([h.path for h in hits])
                syms = _dedupe([g.nodes[h.node_id]["qualname"] for h in hits if h.node_id and h.node_id in g.nodes])
                row.update(tokens=sum(len(h.text) // 4 for h in hits[:k]))
            else:
                r = ask(ctx, q["question"], "graph", True)
                files = _dedupe([h["path"] for h in r["hits"]] + [c["path"] for c in r["citations"] if c["valid"]])
                syms = _dedupe([g.nodes[h["node_id"]]["qualname"] for h in r["hits"] if h.get("node_id") and h["node_id"] in g.nodes])
                text = r["answer"].lower()
                kw = q.get("gold_keywords") or []
                row.update(citation_precision=r["citation_precision"], keyword_coverage=(sum(1 for w in kw if w.lower() in text) / len(kw)) if kw else None,
                           tokens=r["approx_tokens"], provider=r["provider"])
                cited = {c["path"] for c in r["citations"] if c["valid"]}
                row["gold_file_cited"] = (sum(1 for f in q.get("gold_files", []) if f in cited) / len(q["gold_files"])) if q.get("gold_files") else None
                if judge and ctx.llm.available:
                    row["judge"] = _judge(ctx, q, r["answer"])
            row.update(file_recall=_recall(q.get("gold_files", []), files, k), file_mrr=_mrr(q.get("gold_files", []), files),
                       sym_recall=_recall(q.get("gold_symbols", []), syms, k, suffix=True), sym_mrr=_mrr(q.get("gold_symbols", []), syms, suffix=True),
                       latency_ms=int((time.time() - t0) * 1000))
            results[mode].append(row)
    return {"k": k, "n": len(dataset), "per_mode": {m: _summ(rows) for m, rows in results.items()}, "rows": results}


def _judge(ctx, q, answer) -> float | None:
    prompt = (f"Question about a codebase: {q['question']}\nReference facts: files {q.get('gold_files')}, symbols {q.get('gold_symbols')}, keywords {q.get('gold_keywords')}\n"
              f"Candidate answer:\n{answer[:2500]}\n\nScore the answer's correctness and completeness from 1 (wrong) to 5 (fully correct and grounded). Reply with the digit only.")
    try:
        out = ctx.llm.chat([{"role": "user", "content": prompt}], temperature=0, max_tokens=4)
        return float(next(c for c in out if c.isdigit()))
    except Exception:
        return None


def _summ(rows: list[dict]) -> dict:
    def mean(key):
        v = [r[key] for r in rows if r.get(key) is not None]
        return round(statistics.mean(v), 4) if v else None
    return {key: mean(key) for key in ("file_recall", "file_mrr", "sym_recall", "sym_mrr", "citation_precision", "keyword_coverage", "gold_file_cited", "judge", "tokens", "latency_ms")
            if any(r.get(key) is not None for r in rows)}


def to_markdown(res: dict) -> str:
    cols = sorted({c for s in res["per_mode"].values() for c in s})
    lines = [f"QA evaluation: {res['n']} questions, k={res['k']}", "", "| mode | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for m, s in res["per_mode"].items():
        lines.append(f"| {m} | " + " | ".join("-" if s.get(c) is None else str(s[c]) for c in cols) + " |")
    return "\n".join(lines)
