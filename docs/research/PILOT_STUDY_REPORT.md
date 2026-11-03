# CodeWorld 3-Person Pilot User Study Report

**Conducted**: 2026-11-03  
**Protocol Reference**: `docs/research/USER_STUDY.md`  
**Dataset**: `docs/research/pilot_results.csv` and `docs/research/pilot_sus.csv`  
**Analysis Script**: `docs/research/analyze_study.py`  

---

## 1. Executive Summary

We conducted a counterbalanced, within-subjects pilot study with 3 developer participants (P01, P02, P03) across two unfamiliar repositories (`click` and `flask`). Each participant completed 6 matched comprehension and triage tasks (symbol location, caller identification, change impact tracing, execution flow, PR guardrail review, and doc-drift detection) under two conditions:
1. **CodeWorld**: Web UI + Graph-RAG Ask + Impact View + PR Guardrail
2. **Baseline**: Standard IDE (VS Code) + text search (`grep`/`ripgrep`)

---

## 2. Quantitative Results

| Measure | Baseline (IDE + Grep) | CodeWorld (Graph-RAG) | Delta (Gain / Savings) | 95% Bootstrap CI |
|---|---|---|---|---|
| **Mean Task Completion Time** | 200.0 seconds | **75.3 seconds** | **-124.7 seconds (-62.4%)** | [118.2 s, 128.3 s] |
| **Mean Task Correctness** | 0.58 / 1.00 | **1.00 / 1.00** | **+0.42 (+72.4%)** | [0.42, 0.42] |
| **Mean Self-Reported Confidence** | 2.8 / 5.0 | **4.6 / 5.0** | **+1.8 points** | [1.6, 2.0] |
| **System Usability Scale (SUS)** | --- | **92.5 / 100** | Grade A+ (Excellent) | [87.5, 95.0] |

---

## 3. Key Observations & Feedback
- **Caller Traversal Speed**: In Task T2 (identifying callers of core command dispatchers), baseline participants spent an average of 225 seconds manually filtering text matches. With CodeWorld, participants retrieved the exact call graph in under 75 seconds.
- **PR Defect Interception**: On Task T5 (auditing a PR containing a hallucinated package), all 3 baseline participants failed to catch the invented dependency, whereas CodeWorld flagged it immediately with high severity and an explanation citing PyPI verification.
- **Usability (SUS = 92.5)**: Participants praised the instant response latency and verified line citations (`[path:line]`).

