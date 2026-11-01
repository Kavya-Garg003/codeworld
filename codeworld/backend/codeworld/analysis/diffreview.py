"""AI-PR guardrail: graph-aware review of a diff. Catches what code review of AI-generated changes tends to miss."""
from __future__ import annotations
import re
import subprocess

from ..parser import ParseResult
from ..parser.common import JS_EFFECTS, PY_EFFECTS, detect_effects
from . import gitmining, health, importcheck
from .duplicates import similar_to
from .impact import impact
from .security import SEV, SINKS, attack_surface

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "info": 0}


def parse_unified_diff(text: str) -> dict[str, dict]:
    files: dict[str, dict] = {}
    cur, new_ln, old_ln = None, 0, 0
    for line in text.splitlines():
        if line.startswith("diff --git"):
            m = re.match(r"diff --git a/(.*) b/(.*)", line)
            cur = m.group(2) if m else None
            if cur:
                files[cur] = {"added": set(), "removed": set(), "removed_text": [], "added_text": [], "new_file": False, "deleted": False}
        elif line.startswith("+++ ") and cur is None:
            cur = line[4:].strip().removeprefix("b/")
            files[cur] = {"added": set(), "removed": set(), "removed_text": [], "added_text": [], "new_file": False, "deleted": False}
        elif cur and line.startswith("new file mode"):
            files[cur]["new_file"] = True
        elif cur and line.startswith("deleted file mode"):
            files[cur]["deleted"] = True
        elif line.startswith("@@") and cur:
            m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)", line)
            if m:
                old_ln, new_ln = int(m.group(1)), int(m.group(2))
        elif cur and line.startswith("+") and not line.startswith("+++"):
            files[cur]["added"].add(new_ln); files[cur]["added_text"].append(line[1:]); files[cur].setdefault("added_map", {})[new_ln] = line[1:]; new_ln += 1
        elif cur and line.startswith("-") and not line.startswith("---"):
            files[cur]["removed"].add(old_ln); files[cur]["removed_text"].append(line[1:]); old_ln += 1
        elif cur and not line.startswith("\\"):
            new_ln += 1; old_ln += 1
    return files


def git_diff(src, base: str, head: str = "HEAD") -> str:
    if not re.fullmatch(r"[\w./\-~^@]{1,120}", base) or not re.fullmatch(r"[\w./\-~^@]{1,120}", head):
        raise ValueError("invalid ref")
    r = subprocess.run(["git", "-C", str(src), "diff", "--unified=0", "--no-color", f"{base}...{head}"], capture_output=True, timeout=120)
    if r.returncode != 0:
        r = subprocess.run(["git", "-C", str(src), "diff", "--unified=0", "--no-color", base, head], capture_output=True, timeout=120)
    return r.stdout.decode("utf8", "replace")


def _finding(sev, cat, title, detail, path=None, line=None, symbol=None):
    return {"severity": sev, "category": cat, "title": title, "detail": detail, "path": path, "line": line, "symbol": symbol}


def review_diff(ctx, diff_text: str) -> dict:
    g = ctx.graph
    files = parse_unified_diff(diff_text)
    code_files = {p: f for p, f in files.items() if g.node(f"file:{p}") and not f["deleted"]}
    findings: list[dict] = []
    changed: list[str] = []
    for p, f in code_files.items():
        syms = {s for ln in f["added"] for s in [g.enclosing_symbol(p, ln)] if s}
        changed += sorted(syms)
    changed = list(dict.fromkeys(changed))
    prod_changed = [s for s in changed if not g.props(s).get("is_test") and g.kind(s) in ("function", "method")]
    # 1 ---- blast radius ------------------------------------------------------------------------------------
    blast = impact(ctx, changed, depth=5, with_cochange=True, max_graph_nodes=60) if changed else None
    if blast and "error" not in blast:
        c = blast["counts"]
        if blast["risk"]["level"] in ("high", "critical"):
            findings.append(_finding("high" if blast["risk"]["level"] == "critical" else "medium", "blast-radius",
                                     f"Large blast radius ({blast['risk']['level']}, score {blast['risk']['score']})",
                                     f"{c['symbols']} dependent symbols, {c['files']} other files, {c['apis']} endpoints. " + "; ".join(blast["risk"]["reasons"])))
        for cc in blast["cochange"]:
            if not cc["in_static"] and cc["confidence"] >= 0.4 and cc["path"] not in code_files:
                findings.append(_finding("low", "co-change", f"`{cc['path']}` usually changes with `{cc['for']}`",
                                         f"Changed together in {cc['support']} past commits ({int(cc['confidence']*100)}%) but is not part of this diff.", cc["path"]))
    # 2 ---- untested changed code ----------------------------------------------------------------------------
    covered = health.tested_set(g)
    for s in prod_changed:
        if s not in covered and g.props(s).get("loc", 0) >= 3:
            n = g.node(s)
            findings.append(_finding("medium" if g.props(s).get("complexity", 1) >= 5 else "low", "untested-change", f"Changed code has no test reaching it: {n['qualname']}",
                                     "No test calls this function directly or transitively. Add or extend a test.", n["path"], n["start"], n["qualname"]))
    # 3 ---- hallucinated imports / APIs ----------------------------------------------------------------------
    added_lines = {p: f["added"] for p, f in code_files.items()}
    seen_import_titles: set[str] = set()
    for h in importcheck.check_imports(ctx, added_lines):
        key = (h["path"], h["title"])
        if key not in seen_import_titles:
            seen_import_titles.add(key)
            findings.append(_finding(h["severity"], h["category"], h["title"], h["detail"], h["path"], h["line"]))
    # Also check directly from diff text (catches cases where git apply didn't update the index on Windows)
    for h in importcheck.check_diff_imports(ctx, code_files):
        key = (h["path"], h["title"])
        if key not in seen_import_titles:
            seen_import_titles.add(key)
            findings.append(_finding(h["severity"], h["category"], h["title"], h["detail"], h["path"], h["line"]))
    # 4 ---- architecture drift: layering + cycles --------------------------------------------------------------
    for v in health.layering_violations(ctx, set(code_files)):
        if v["line"] in code_files[v["from"]]["added"]:
            findings.append(_finding("high", "layering", f"New forbidden dependency {v['from']} -> {v['to']}", v["rule"], v["from"], v["line"]))
    for cyc in health.import_cycles(g):
        hit = [p for p in cyc if p in code_files]
        if hit:
            findings.append(_finding("medium", "import-cycle", "Import cycle involves changed files", " -> ".join(cyc + [cyc[0]]), hit[0]))
    # 5 ---- duplicated logic (missed reuse) ---------------------------------------------------------------------
    with ctx.con() as con:
        rows = [dict(r) for r in con.execute("SELECT node_id, path, name, start, end, text FROM chunks WHERE kind IN ('function','method') AND node_id IS NOT NULL")]
    for s in prod_changed:
        n = g.node(s)
        mine = next((r for r in rows if r["node_id"] == s), None)
        if not mine or n["props"].get("loc", 0) < 5:
            continue
        for d in similar_to(mine["text"], [r for r in rows if not g.props(r["node_id"]).get("is_test")], {s}):
            findings.append(_finding("medium", "duplicate-logic", f"`{n['qualname']}` closely duplicates `{d['name']}` ({int(d['similarity']*100)}% similar)",
                                     f"Consider reusing `{d['name']}` ({d['path']}:{d['start']}) instead of adding a copy.", n["path"], n["start"], n["qualname"]))
    # 5b ---- also check new functions extracted directly from diff text (robust when git apply doesn't update the index)
    _py_func_hdr = re.compile(r"^[\+]?\s*(?:async\s+)?def\s+(\w+)\s*\(")
    for path, finfo in code_files.items():
        if not path.endswith(".py"):
            continue
        added_text = finfo.get("added_text", [])
        func_body: list[str] = []
        func_name: str | None = None
        func_start: int = 0
        added_sorted = sorted(finfo.get("added", set()))
        def _flush_func():
            nonlocal func_body, func_name, func_start
            if func_name and len(func_body) >= 5:
                synth_chunk = {"node_id": f"diff:{path}:{func_name}", "name": func_name,
                               "path": path, "start": func_start, "end": func_start + len(func_body),
                               "text": "\n".join(func_body)}
                existing_ids = {s for s in prod_changed}
                for d in similar_to(synth_chunk["text"], [r for r in rows if not g.props(r["node_id"]).get("is_test")], existing_ids):
                    findings.append(_finding("medium", "duplicate-logic",
                                             f"`{func_name}` (new in diff) closely duplicates `{d['name']}` ({int(d['similarity']*100)}% similar)",
                                             f"Consider reusing `{d['name']}` ({d['path']}:{d['start']}) instead of adding a copy.",
                                             path, func_start, func_name))
            func_body, func_name = [], None
        for idx, line in enumerate(added_text):
            ln = added_sorted[idx] if idx < len(added_sorted) else 0
            m = _py_func_hdr.match(line)
            if m:
                _flush_func()
                func_name = m.group(1)
                func_start = ln
                func_body = [line.lstrip("+")]
            elif func_name:
                func_body.append(line.lstrip("+"))
        _flush_func()
    # 6 ---- risky sinks reachable from endpoints ------------------------------------------------------------------
    surf = {r["handler"]: r for r in attack_surface(ctx)}
    for s in changed:
        n = g.node(s)
        eff = [e for e in (n["props"].get("effects") or []) if e in SINKS and SEV[SINKS[e][0]] >= 2]
        added_here = [t for ln, t in (code_files.get(n["path"], {}).get("added_map", {}) or {}).items() if n["start"] <= ln <= n["end"]]
        introduced = set()
        for t in added_here:                        # sinks only count as NEW when an added line itself performs the call
            for callee in re.findall(r"[\w.]+(?=\()", t):
                introduced.update(detect_effects(callee, PY_EFFECTS + JS_EFFECTS))
        for e in eff:
            reach = [a["api"] for a in surf.values() if any(r["symbol"] == n["qualname"] for r in a["risks"])]
            new = e in introduced
            sev = ("high" if SEV[SINKS[e][0]] >= 3 else "medium") if new else "low"
            title = f"{'New' if new else 'Existing'} `{e}` sink in changed function: {n['qualname']}"
            findings.append(_finding(sev, "security-sink", title,
                                     SINKS[e][1] + ("" if new else " (already present before this change; touched code only)") + (f". Reachable from: {', '.join(reach[:4])}" if reach else ""),
                                     n["path"], n["start"], n["qualname"]))
    # 7 ---- removed symbols that are still referenced ---------------------------------------------------------------
    still_defined = {n["name"] for n in g.nodes.values() if n["kind"] in ("function", "method", "class")}
    removed_defs: dict[str, str] = {}
    for p, f in files.items():
        added_blob = "\n".join(f["added_text"])
        for t in f["removed_text"]:
            m = re.match(r"\s*(?:async\s+)?(?:def|class|function)\s+(\w+)", t)
            if m and m.group(1) not in still_defined and not re.search(rf"\b{m.group(1)}\b", added_blob):
                removed_defs[m.group(1)] = p
    if removed_defs:
        with ctx.con() as con:
            for r in con.execute("SELECT path, json FROM parsed"):
                pr = ParseResult.from_json(r["json"])
                for c in pr.calls:
                    last = c.text.split(".")[-1]
                    if last in removed_defs:
                        findings.append(_finding("high", "dangling-reference", f"`{last}` was removed but is still called",
                                                 f"Removed in {removed_defs[last]}; still referenced at {pr.path}:{c.line}.", pr.path, c.line))
    # 8 ---- complexity growth -------------------------------------------------------------------------------------------
    for s in prod_changed:
        cx = g.props(s).get("complexity", 1)
        if cx >= 15:
            n = g.node(s)
            findings.append(_finding("low", "complexity", f"High cyclomatic complexity ({cx}): {n['qualname']}", "Consider splitting this function.", n["path"], n["start"], n["qualname"]))
    findings.sort(key=lambda f: -SEVERITY_ORDER[f["severity"]])
    seen, uniq = set(), []
    for f in findings:
        k = (f["category"], f["title"], f["path"], f["line"])
        if k not in seen:
            seen.add(k); uniq.append(f)
    counts = {s: sum(1 for f in uniq if f["severity"] == s) for s in ("high", "medium", "low")}
    verdict = "fail" if counts["high"] else "warn" if counts["medium"] else "pass"
    report = {"verdict": verdict, "counts": counts, "findings": uniq,
              "changed_files": sorted(files), "changed_symbols": [g.nodes[s]["qualname"] for s in changed],
              "blast_radius": {k: blast[k] for k in ("risk", "counts", "apis", "tests", "likely_tests", "files")} if blast and "error" not in blast else None,
              "graph": blast["graph"] if blast and "error" not in blast else {"nodes": [], "edges": []}}
    report["markdown"] = to_markdown(report, emoji=False)
    return report


def to_markdown(r: dict, emoji: bool = True) -> str:
    import sys
    # Use emoji only when explicitly requested or when stdout supports it;
    # .md file output (emoji=False) uses ASCII-safe alternatives so Windows read_text() works.
    _safe = emoji and getattr(sys.stdout, "encoding", "ascii").lower().replace("-", "") in ("utf8", "utf16", "utf32")
    icon = {"pass": "\u2705" if _safe else "[PASS]",
            "warn": "\u26a0\ufe0f" if _safe else "[WARN]",
            "fail": "\u274c" if _safe else "[FAIL]"}[r["verdict"]]
    out = [f"## {icon} CodeWorld PR Guardrail: **{r['verdict'].upper()}**",
           f"{r['counts']['high']} high · {r['counts']['medium']} medium · {r['counts']['low']} low | {len(r['changed_files'])} files, {len(r['changed_symbols'])} symbols changed", ""]
    b = r.get("blast_radius")
    if b:
        out += [f"**Blast radius:** {b['risk']['level']} ({b['risk']['score']}/100): {b['counts']['symbols']} dependent symbols, {b['counts']['files']} files, "
                f"{b['counts']['apis']} endpoints, {b['counts']['tests']} tests reach this change.", ""]
        if b["tests"]:
            out += ["**Run these tests first:** " + ", ".join(f"`{t['name']}`" for t in b["tests"][:8]), ""]
    for sev in ("high", "medium", "low"):
        items = [f for f in r["findings"] if f["severity"] == sev]
        if items:
            out.append(f"### {sev.title()} severity")
            for f in items[:25]:
                loc = f" (`{f['path']}:{f['line']}`)" if f["path"] and f["line"] else (f" (`{f['path']}`)" if f["path"] else "")
                out.append(f"- **{f['title']}**{loc}: {f['detail']}")
            out.append("")
    if not r["findings"]:
        out.append("No issues found by graph checks.")
    return "\n".join(out)


def review_refs(ctx, base: str, head: str = "HEAD") -> dict:
    return review_diff(ctx, git_diff(ctx.ref.src, base, head))


def review_patch(ctx, diff_text: str) -> dict:
    """Review a pasted diff against the *currently indexed snapshot* (treated as the base).

    The snapshot is copied to a scratch directory, the patch is applied (never executed), the scratch copy is re-indexed
    incrementally, and the guardrail runs on the resulting 'head' graph. The original index is never modified.
    """
    import shutil
    import sqlite3
    import tempfile
    from pathlib import Path

    from ..config import get_settings
    from ..indexer import index_repo
    from ..ingest import IGNORE_DIRS, RepoRef
    from ..service import RepoContext

    s = get_settings()
    tmp = Path(tempfile.mkdtemp(prefix="cw_review_"))
    try:
        src = tmp / "src"
        shutil.copytree(ctx.ref.src, src, ignore=shutil.ignore_patterns(*IGNORE_DIRS), symlinks=False)
        patch = tmp / "change.diff"
        patch.write_text(diff_text if diff_text.endswith("\n") else diff_text + "\n", encoding="utf8")
        r = subprocess.run(["git", "apply", "--unidiff-zero", "--whitespace=nowarn", "--recount", str(patch)], cwd=src, capture_output=True, timeout=60)
        if r.returncode != 0:
            rep = review_diff(ctx, diff_text)
            rep["note"] = ("Patch could not be applied to the indexed snapshot (" + r.stderr.decode("utf8", "replace")[:160].strip() +
                           "). Reviewed against the current index instead - make sure the index contains the PR head.")
            return rep
        db = tmp / "index.db"
        with sqlite3.connect(str(ctx.ref.db)) as a, sqlite3.connect(str(db)) as b:
            a.backup(b)
        ref = RepoRef(f"review-{tmp.name}", ctx.ref.name, tmp, src, db)
        index_repo(s, ref)
        tctx = RepoContext(s, ref)
        rep = review_diff(tctx, diff_text)
        rep["note"] = "Patch applied to a scratch copy of the indexed snapshot and re-indexed; your index was not modified."
        rep["markdown"] = rep["markdown"] + "\n\n_" + rep["note"] + "_"
        return rep
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
