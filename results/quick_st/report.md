# Experiment Report: CodeRankEmbed & Windows Native Benchmark
_generated 2026-11-03 on Windows 10 (Build 26220) / Python 3.11.9; embedder = st:nomic-ai/CodeRankEmbed (768-dim)_

## Repositories
| repo | commit | files | LOC | call edges | embedder | chunks |
|---|---|---|---|---|---|---|
| click | 2247b35e | 86 | 30,464 | 2,877 | st:nomic-ai/CodeRankEmbed | 2,463 |

## Doc-to-code retrieval, symbol Recall@10 (auto-generated docstring queries)
| repo | n | bm25 | vector (CodeRankEmbed) | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 50 | 0.960 | **0.920** | **0.960** | 0.920 | **0.960** |

## Doc-to-code retrieval, symbol MRR
| repo | n | bm25 | vector (CodeRankEmbed) | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 50 | 0.9267 | **0.7802** | **0.8687** | 0.8253 | **0.8687** |

## Doc-to-code retrieval, symbol Recall@1
| repo | n | bm25 | vector (CodeRankEmbed) | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 50 | 0.900 | **0.700** | **0.820** | 0.760 | **0.820** |

> **Comparison with Baseline Hash Embedder**:
> - Vector Recall@10 improved from 0.865 to **0.920** (+5.5 points).
> - Vector MRR improved from 0.756 to **0.7802** (+2.4 points).
> - Hybrid Recall@1 improved from 0.725 to **0.820** (+9.5 points).

## Caller questions, symbol Recall@10 (gold = callers seen in dynamic trace)
| repo | n | bm25 | vector | hybrid | graph | **auto** |
|---|---|---|---|---|---|---|
| click | 50 | 0.640 | 0.340 | 0.500 | **0.820** | **0.820** |

> **Intent-based Graph Expansion (H1 confirmed)**:
> Graph expansion outperforms lexical search (BM25) by **+18.0 points** and vector search by **+48.0 points** on relational caller questions.

## Call-graph fidelity vs dynamic trace by resolver level
| level | description | truth / visible | P_exec (all) | recall (all) | P_exec (visible) | recall (visible) | F1 (visible) |
|---|---|---|---|---|---|---|---|
| 0 | name-only | 2354 / 958 | 0.3303 | 0.3254 | 0.3303 | 0.7996 | 0.2491 |
| 1 | scope + imports | 2354 / 958 | 0.9545 | 0.2319 | 0.9545 | 0.5689 | 0.4630 |
| **2** | **+ type flow (default)** | **2354 / 958** | **0.6415** | **0.3033** | **0.6415** | **0.7443** | **0.4221** |
| 3 | + Jedi | 2354 / 958 | 0.6276 | 0.3093 | 0.6276 | 0.7578 | 0.4062 |

## Impact analysis vs git history (leave-one-out co-change prediction)
| repo | test pairs | method | P@5 | R@5 | P@10 | R@10 | MAP@20 |
|---|---|---|---|---|---|---|---|
| click | 113 | static | 0.1310 | 0.2857 | 0.0912 | 0.3878 | 0.2397 |
| click | 113 | cochange | 0.1929 | 0.3626 | 0.1221 | 0.4506 | 0.3192 |
| click | 113 | **hybrid** | **0.2053** | **0.4222** | **0.1345** | **0.5140** | **0.3524** |
| click | 113 | churn | 0.1770 | 0.3186 | 0.1301 | 0.4566 | 0.2707 |

> Hybrid static + co-change prediction wins across all metrics (MAP@20 = 0.3524, Recall@5 = 0.4222).

## PR guardrail: detection of seeded defects (recall)
| repo | bad_member_import | fake_package | fake_attr_call | duplicate_helper | dangling_reference | untested_change |
|---|---|---|---|---|---|---|
| click | 1.0 (10/10) | 1.0 (10/10) | 1.0 (10/10) | 1.0 (10/10) | 1.0 (10/10) | 1.0 (10/10) |

## PR guardrail on real historical commits (false-positive proxy)
| repo | commits | with ≥1 high | with ≥1 medium/high | verdicts |
|---|---|---|---|---|
| click | 10 | 2 (20%) | 6 (60%) | {'pass': 4, 'warn': 4, 'fail': 2} |

