"""`codeworld eval ...` dispatcher."""
from __future__ import annotations
import json
import sys
from pathlib import Path

from ..indexer import index_repo
from . import callgraph_eval, impact_eval, qa_eval


def _emit(obj, out: str | None, md: str | None = None):
    text = json.dumps(obj, indent=2, default=str)
    print(md or text)
    if out:
        Path(out).write_text(text)
        print(f"\nsaved {out}", file=sys.stderr)


def run(settings, a):
    from ..cli import _repo
    ctx = _repo(settings, a.repo)
    if a.what == "qa":
        ds = json.loads(Path(a.dataset or Path(__file__).parent / "datasets" / "shop_app_qa.json").read_text())
        res = qa_eval.evaluate(ctx, ds, [m.strip() for m in a.modes.split(",")], a.k)
        _emit(res, a.out, qa_eval.to_markdown(res))
    elif a.what == "impact":
        res = impact_eval.evaluate(ctx, a.commits)
        _emit(res, a.out)
    elif a.what == "callgraph":
        if not a.truth:
            sys.exit("--truth <edges.json> is required (see codeworld.evaluation.dynamic_trace)")
        _emit(callgraph_eval.evaluate(ctx, a.truth), a.out)
    elif a.what == "resolver-ablation":
        from ..ingest import repo_ref
        ref = ctx.ref
        table = {}
        for lv in (0, 1, 2, 3):
            index_repo(settings, ref, level=lv, force=True)
            ctx._version = None
            row = {}
            if a.truth:
                row["callgraph"] = callgraph_eval.evaluate(ctx, a.truth, levels=(lv,))["levels"][f"level{lv}"]
            if a.dataset:
                ds = json.loads(Path(a.dataset).read_text())
                row["qa"] = qa_eval.evaluate(ctx, ds, ["graph"], a.k)["per_mode"]["graph"]
            table[f"level{lv}"] = row
        index_repo(settings, ref, level=settings.resolver_level, force=True)
        _emit(table, a.out)
