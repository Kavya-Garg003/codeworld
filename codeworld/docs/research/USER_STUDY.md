# User study protocol (RQ5)

**Question**: Does CodeWorld reduce time and errors on codebase-comprehension tasks?
**Design**: within-subjects, counterbalanced. Each participant solves matched task sets on two *unfamiliar* repositories (A, B): one with CodeWorld (UI + Ask), one with their usual tools (IDE + grep + browser; optionally their normal AI assistant - decide and state it up front). Half start with CodeWorld, half without; repository/condition assignment is rotated (AB/BA × tool order).
**Participants**: 12-20 students/early-career developers (Python familiarity), recruited from classmates/juniors; no prior exposure to the repos. Pre-register the sample size and analysis.
**Tasks (per repository, 6 tasks, 10 min cap each)** - see `tasks_template.md`; gold answers written before the study by someone who is not a participant.
**Measures**: task time, correctness (0/1/partial rubric, graded blind to condition), self-reported confidence (1-5), SUS (10 items, after the CodeWorld condition), NASA-TLX raw (optional), free-text comments.
**Procedure**: consent → 5-minute CodeWorld tutorial (script it) → condition 1 → break → condition 2 → SUS + interview. Screen-record with consent. Pilot with 2 people and fix task wording.
**Ethics**: informed consent, voluntary, anonymised IDs, no grades attached, data kept off public repos; check whether your institution needs ethics-committee approval for human-subject research.
**Analysis**: `analyze_study.py results.csv` (paired differences, bootstrap CI, Wilcoxon if SciPy is installed, SUS score). Report medians + CIs, not just p-values. Qualitative: thematic coding of comments by two coders.
**Threats**: learning effects (counterbalance), task-difficulty mismatch (pilot, matched pairs), experimenter bias (blind grading), novelty effect, small n (say so).

## results.csv columns
`participant,condition(codeworld|baseline),repo,task_id,seconds,correct(0..1),confidence(1..5)`
and a separate `sus.csv`: `participant,q1..q10` (1-5).

> The `*_example.csv` files are made-up illustrations of the format, not data.
