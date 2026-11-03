# Experiment report
_generated 2026-11-02 02:18 on Windows-10-10.0.26220-SP0 / Python 3.11.9; embedder = hash_

## Repositories
| repo | commit | files | LOC | call edges | index s | peak RSS MB |
|---|---|---|---|---|---|---|
| click | 2247b35e | 86 | 30,464 | 2,877 | 16.88 | 0 |

## Doc-to-code retrieval, symbol Recall@10 (auto-generated queries)
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.945 | 0.865 | 0.925 | 0.91 | 0.925 |

## Doc-to-code retrieval, symbol MRR
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.8648 | 0.756 | 0.8068 | 0.7839 | 0.8068 |

## Doc-to-code retrieval, symbol Recall@1
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.82 | 0.7 | 0.725 | 0.705 | 0.725 |

## Impact analysis vs git history (leave-one-out, time-split)
| repo | test pairs | method | P@5 | R@5 | P@10 | R@10 | MAP@20 |
|---|---|---|---|---|---|---|---|
| click | 342 | static | 0.1585 | 0.3754 | 0.1053 | 0.4722 | 0.3223 |
| click | 342 | cochange | 0.2012 | 0.4234 | 0.1439 | 0.5517 | 0.3884 |
| click | 342 | hybrid | 0.207 | 0.4696 | 0.1409 | 0.5823 | 0.3984 |
| click | 342 | churn | 0.1942 | 0.3392 | 0.152 | 0.5424 | 0.3659 |

Share of truly co-changed files (top-10 predictions): click: both 21%, only_static 9%, only_cochange 20%, neither 50%

## PR guardrail: detection of seeded defects (recall)
| repo | bad_member_import | fake_package | fake_attr_call | duplicate_helper | dangling_reference | untested_change |
|---|---|---|---|---|---|---|
| click | 1.0 (20/20) | 1.0 (20/20) | 1.0 (20/20) | 1.0 (20/20) | 1.0 (5/5) | 1.0 (9/9) |

## PR guardrail on real historical commits (false-positive proxy)
| repo | commits | with ≥1 high | with ≥1 medium/high | verdicts |
|---|---|---|---|---|
| click | 25 | 2 | 13 | {'warn': 11, 'fail': 2, 'pass': 12} |
