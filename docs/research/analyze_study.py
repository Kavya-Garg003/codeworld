"""Analyse the user study. Usage: python analyze_study.py results.csv [sus.csv]"""
import csv, math, random, statistics, sys
from collections import defaultdict


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def boot_ci(xs, n=5000, seed=1):
    rnd = random.Random(seed)
    means = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def main():
    rows = load(sys.argv[1])
    per = defaultdict(lambda: defaultdict(list))
    for r in rows:
        per[r["participant"]][r["condition"]].append(r)
    diffs_t, diffs_c = [], []
    for p, d in per.items():
        if "codeworld" in d and "baseline" in d:
            t = lambda cs: statistics.mean(float(x["seconds"]) for x in d[cs])
            c = lambda cs: statistics.mean(float(x["correct"]) for x in d[cs])
            diffs_t.append(t("baseline") - t("codeworld"))      # positive = CodeWorld faster
            diffs_c.append(c("codeworld") - c("baseline"))      # positive = CodeWorld more correct
    print(f"participants with both conditions: {len(diffs_t)}")
    for name, xs, unit in (("time saved (s)", diffs_t, "s"), ("correctness gain", diffs_c, "")):
        if len(xs) >= 2:
            lo, hi = boot_ci(xs)
            print(f"{name}: mean {statistics.mean(xs):.2f}{unit}  median {statistics.median(xs):.2f}  95% bootstrap CI [{lo:.2f}, {hi:.2f}]")
            try:
                from scipy.stats import wilcoxon
                print(f"   Wilcoxon signed-rank p = {wilcoxon(xs).pvalue:.4f}")
            except Exception:
                print("   (install scipy for the Wilcoxon test)")
    if len(sys.argv) > 2:
        scores = []
        for r in load(sys.argv[2]):
            q = [int(r[f"q{i}"]) for i in range(1, 11)]
            scores.append((sum(x - 1 for x in q[0::2]) + sum(5 - x for x in q[1::2])) * 2.5)
        print(f"SUS: mean {statistics.mean(scores):.1f} (n={len(scores)}); >68 is above average usability")


if __name__ == "__main__":
    main()
