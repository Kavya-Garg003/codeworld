"""RQ2: call-graph resolution fidelity vs ground truth (e.g. produced by dynamic_trace.py or hand-labelled)."""
from __future__ import annotations
import json
from pathlib import Path

from ..graph.builder import GraphBuilder
from ..parser import ParseResult


def predicted_edges(parsed, level: int, root: Path | None, min_conf: float) -> set[tuple[str, str]]:
    nodes, edges, _ = GraphBuilder(parsed, level=level, root=root).build()
    kinds = {n["id"]: n for n in nodes}
    out = set()
    for (s, d, t), (conf, res, line) in edges.items():
        if t != "CALLS" or conf < min_conf:
            continue
        sn, dn = kinds.get(s), kinds.get(d)
        if sn and dn and sn["kind"] in ("function", "method", "test") and dn["kind"] in ("function", "method", "test"):
            out.add((f"{sn['path']}::{sn['qualname']}", f"{dn['path']}::{dn['qualname']}"))
    return out


def prf(pred: set, truth: set) -> dict:
    """Dynamic traces are an *under-approximation*: unexecuted edges are not 'wrong'. So besides plain precision we report
    precision restricted to callers that actually executed (still a lower bound) - use manual labels for exact precision."""
    tp = len(pred & truth)
    executed = {a for a, _ in truth}
    pred_exec = {e for e in pred if e[0] in executed}
    p_exec = len(pred_exec & truth) / len(pred_exec) if pred_exec else 0.0
    p = tp / len(pred) if pred else 0.0
    r = tp / len(truth) if truth else 0.0
    return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(2 * p * r / (p + r), 4) if p + r else 0.0, "precision_executed_callers": round(p_exec, 4),
            "predicted": len(pred), "truth": len(truth), "tp": tp}


def evaluate(ctx, truth_path: str, levels=(0, 1, 2, 3), min_conf: float = 0.0) -> dict:
    truth = {tuple(x) for x in json.loads(Path(truth_path).read_text())}
    with ctx.con() as con:
        parsed = {r["path"]: ParseResult.from_json(r["json"]) for r in con.execute("SELECT path, json FROM parsed")}
    # restrict truth to files we parsed (the tracer may see third-party frames)
    truth = {(a, b) for a, b in truth if a.split("::")[0] in parsed and b.split("::")[0] in parsed}
    # Dynamic traces also contain *implicit* calls (decorators, properties, dunder protocols, callbacks invoked by the framework).
    # A static analyser that follows call syntax cannot be expected to find those, so we also report the "syntactically visible" subset.
    names = {}
    for pr in parsed.values():
        for c in pr.calls:
            names.setdefault(c.caller, set()).add(c.text.split(".")[-1])
    visible = set()
    for a, b in truth:
        q = b.split("::", 1)[1].split(".")
        cn, cls = q[-1], (q[-2] if len(q) > 1 else None)
        ns = names.get(f"sym:{a}", set())
        if cn in ns or (cn == "__init__" and cls in ns):
            visible.add((a, b))
    out = {}
    for lv in levels:
        pred = predicted_edges(parsed, lv, ctx.ref.src, min_conf)
        out[f"level{lv}"] = {**prf(pred, truth), "visible": prf(pred, visible)}
    return {"truth_edges": len(truth), "visible_edges": len(visible), "levels": out,
            "note": "level0=name-only, 1=scope+imports, 2=+type flow, 3=+Jedi; 'visible' = observed calls that have a matching call expression in the caller"}
