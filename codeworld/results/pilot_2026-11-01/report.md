# Experiment report
_generated 2026-11-01 16:27 on Linux-6.18.44-fc-v185-x86_64-with-glibc2.39 / Python 3.12.3; embedder = hash_

## Repositories
| repo | commit | files | LOC | call edges | index s | peak RSS MB |
|---|---|---|---|---|---|---|
| click | 2247b35e | 86 | 30,464 | 2,877 | 7.91 | 91 |
| flask | 49943b5a | 80 | 18,472 | 1,557 | 10.81 | 117 |
| jinja | 5ef70112 | 59 | 22,934 | 4,404 | 4.79 | 136 |
| requests | 3c7baaa0 | 36 | 12,068 | 1,157 | 3.44 | 149 |
| rich | 9d8f9a37 | 211 | 52,077 | 4,918 | 9.51 | 179 |

## Doc-to-code retrieval, symbol Recall@10 (auto-generated queries)
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.945 | 0.865 | 0.925 | 0.91 | 0.925 |
| flask | 200 | 0.965 | 0.88 | 0.95 | 0.91 | 0.95 |
| jinja | 200 | 0.94 | 0.905 | 0.955 | 0.935 | 0.955 |
| requests | 122 | 0.9836 | 0.877 | 0.9508 | 0.9344 | 0.9508 |
| rich | 200 | 0.92 | 0.83 | 0.89 | 0.865 | 0.89 |
| **mean** | | **0.951** | **0.871** | **0.934** | **0.911** | **0.934** |

## Doc-to-code retrieval, symbol MRR
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.8648 | 0.756 | 0.8068 | 0.7836 | 0.8068 |
| flask | 200 | 0.8025 | 0.7101 | 0.7558 | 0.7147 | 0.755 |
| jinja | 200 | 0.8323 | 0.7703 | 0.7897 | 0.7487 | 0.7897 |
| requests | 122 | 0.8713 | 0.749 | 0.8198 | 0.7947 | 0.8198 |
| rich | 200 | 0.75 | 0.6335 | 0.7079 | 0.6825 | 0.7079 |
| **mean** | | **0.824** | **0.724** | **0.776** | **0.745** | **0.776** |

## Doc-to-code retrieval, symbol Recall@1
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 200 | 0.82 | 0.7 | 0.725 | 0.705 | 0.725 |
| flask | 200 | 0.72 | 0.635 | 0.66 | 0.6 | 0.66 |
| jinja | 200 | 0.77 | 0.69 | 0.7 | 0.64 | 0.7 |
| requests | 122 | 0.8033 | 0.6803 | 0.7377 | 0.7049 | 0.7377 |
| rich | 200 | 0.66 | 0.54 | 0.605 | 0.565 | 0.605 |
| **mean** | | **0.755** | **0.649** | **0.686** | **0.643** | **0.686** |

## Caller questions, symbol Recall@10 (gold = callers seen in a dynamic trace)
| repo | n | bm25 | vector | hybrid | graph | auto |
|---|---|---|---|---|---|---|
| click | 100 | 0.68 | 0.58 | 0.66 | 0.84 | 0.84 |
| flask | 100 | 0.49 | 0.37 | 0.42 | 0.57 | 0.57 |
| jinja | 100 | 0.44 | 0.34 | 0.4 | 0.63 | 0.63 |
| requests | 98 | 0.7653 | 0.5816 | 0.7245 | 0.949 | 0.949 |
| rich | 100 | 0.56 | 0.33 | 0.48 | 0.72 | 0.72 |
| **mean** | | **0.587** | **0.44** | **0.537** | **0.742** | **0.742** |

## Call-graph fidelity vs dynamic trace by resolver level
Recall is exact w.r.t. observed calls; precision is only a lower bound (unexecuted edges count as wrong). `P_exec` = precision restricted to callers that actually ran.

`visible` = the subset of observed calls that have a matching call expression in the caller's source (excludes decorators, properties, dunder protocols, framework callbacks).

| repo | truth / visible edges | level | P_exec (all) | recall (all) | P_exec (visible) | recall (visible) | F1 (visible) |
|---|---|---|---|---|---|---|---|
| click | 2354 / 958 | level0 | 0.3303 | 0.3254 | 0.3361 | 0.7996 | 0.2491 |
| click | 2354 / 958 | level1 | 0.9545 | 0.2319 | 0.9561 | 0.5689 | 0.463 |
| click | 2354 / 958 | level2 | 0.6415 | 0.3033 | 0.6452 | 0.7443 | 0.4221 |
| click | 2354 / 958 | level3 | 0.6276 | 0.3093 | 0.633 | 0.7578 | 0.4062 |
| flask | 1555 / 477 | level0 | 0.1719 | 0.2322 | 0.2548 | 0.7568 | 0.1613 |
| flask | 1555 / 477 | level1 | 0.6617 | 0.2013 | 0.8067 | 0.6562 | 0.4929 |
| flask | 1555 / 477 | level2 | 0.5648 | 0.272 | 0.6609 | 0.8868 | 0.4679 |
| flask | 1555 / 477 | level3 | 0.5574 | 0.2875 | 0.6448 | 0.9287 | 0.4708 |
| jinja | 2110 / 1552 | level0 | 0.5601 | 0.636 | 0.5679 | 0.8647 | 0.4865 |
| jinja | 2110 / 1552 | level1 | 0.9339 | 0.3147 | 0.8876 | 0.4021 | 0.4638 |
| jinja | 2110 / 1552 | level2 | 0.6562 | 0.7265 | 0.6433 | 0.962 | 0.5594 |
| jinja | 2110 / 1552 | level3 | 0.6235 | 0.7393 | 0.6129 | 0.9762 | 0.5424 |
| requests | 372 / 244 | level0 | 0.4824 | 0.5538 | 0.5061 | 0.8443 | 0.2089 |
| requests | 372 / 244 | level1 | 0.9016 | 0.6156 | 0.8704 | 0.8811 | 0.4757 |
| requests | 372 / 244 | level2 | 0.8249 | 0.6586 | 0.8105 | 0.9467 | 0.4049 |
| requests | 372 / 244 | level3 | 0.8218 | 0.6694 | 0.8103 | 0.9631 | 0.3997 |
| rich | 1652 / 1039 | level0 | 0.3614 | 0.4159 | 0.3804 | 0.6612 | 0.2121 |
| rich | 1652 / 1039 | level1 | 0.9354 | 0.368 | 0.941 | 0.5833 | 0.4198 |
| rich | 1652 / 1039 | level2 | 0.9178 | 0.5811 | 0.9247 | 0.922 | 0.474 |
| rich | 1652 / 1039 | level3 | 0.9224 | 0.6041 | 0.9291 | 0.9586 | 0.4814 |

## Impact analysis vs git history (leave-one-out, time-split)
| repo | test pairs | method | P@5 | R@5 | P@10 | R@10 | MAP@20 |
|---|---|---|---|---|---|---|---|
| click | 342 | static | 0.1579 | 0.3767 | 0.1061 | 0.4706 | 0.3242 |
| click | 342 | cochange | 0.2012 | 0.4234 | 0.1439 | 0.5517 | 0.3884 |
| click | 342 | hybrid | 0.2094 | 0.4724 | 0.1395 | 0.5749 | 0.3967 |
| click | 342 | churn | 0.1942 | 0.3392 | 0.152 | 0.5424 | 0.3659 |
| flask | 338 | static | 0.2308 | 0.2567 | 0.1893 | 0.3551 | 0.2217 |
| flask | 338 | cochange | 0.2935 | 0.2653 | 0.2358 | 0.3976 | 0.3029 |
| flask | 338 | hybrid | 0.3071 | 0.3163 | 0.2527 | 0.4515 | 0.324 |
| flask | 338 | churn | 0.3095 | 0.2966 | 0.226 | 0.431 | 0.3016 |
| jinja | 213 | static | 0.3296 | 0.2512 | 0.2653 | 0.3747 | 0.2625 |
| jinja | 213 | cochange | 0.3981 | 0.1985 | 0.3784 | 0.3959 | 0.3844 |
| jinja | 213 | hybrid | 0.4319 | 0.3346 | 0.3399 | 0.4327 | 0.3897 |
| jinja | 213 | churn | 0.3174 | 0.2121 | 0.2808 | 0.3864 | 0.2351 |
| requests | 62 | static | 0.4032 | 0.4886 | 0.3516 | 0.7382 | 0.5139 |
| requests | 62 | cochange | 0.271 | 0.1599 | 0.279 | 0.328 | 0.3276 |
| requests | 62 | hybrid | 0.4194 | 0.4079 | 0.3694 | 0.6647 | 0.4947 |
| requests | 62 | churn | 0.0839 | 0.1613 | 0.1323 | 0.3548 | 0.2177 |
| rich | 426 | static | 0.1197 | 0.2933 | 0.0744 | 0.3413 | 0.2228 |
| rich | 426 | cochange | 0.1282 | 0.3396 | 0.0833 | 0.3995 | 0.2865 |
| rich | 426 | hybrid | 0.1559 | 0.3878 | 0.096 | 0.4467 | 0.3093 |
| rich | 426 | churn | 0.0859 | 0.1534 | 0.0749 | 0.277 | 0.134 |

Share of truly co-changed files (top-10 predictions): click: both 21%, only_static 9%, only_cochange 20%, neither 50%; flask: both 11%, only_static 16%, only_cochange 23%, neither 49%; jinja: both 16%, only_static 13%, only_cochange 26%, neither 45%; requests: both 21%, only_static 34%, only_cochange 23%, neither 22%; rich: both 5%, only_static 4%, only_cochange 5%, neither 86%

## PR guardrail: detection of seeded defects (recall)
| repo | bad_member_import | fake_package | fake_attr_call | duplicate_helper | dangling_reference | untested_change |
|---|---|---|---|---|---|---|
| click | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (5/5) | 1.0 (6/6) |
| flask | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (2/2) | 1.0 (8/8) |
| jinja | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (3/3) | 1.0 (11/11) |
| requests | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 1.0 (15/15) | 0.5 (3/6) | 1.0 (4/4) |
| rich | 1.0 (13/13) | 1.0 (15/15) | 1.0 (13/13) | 1.0 (15/15) | 1.0 (7/7) | 1.0 (4/4) |

## PR guardrail on real historical commits (false-positive proxy)
| repo | commits | with ≥1 high | with ≥1 medium/high | verdicts |
|---|---|---|---|---|
| click | 20 | 1 | 9 | {'warn': 8, 'pass': 11, 'fail': 1} |
| flask | 20 | 0 | 12 | {'warn': 12, 'pass': 8} |
| jinja | 20 | 0 | 5 | {'pass': 15, 'warn': 5} |
| requests | 20 | 0 | 7 | {'warn': 7, 'pass': 13} |
| rich | 20 | 0 | 9 | {'pass': 11, 'warn': 9} |
