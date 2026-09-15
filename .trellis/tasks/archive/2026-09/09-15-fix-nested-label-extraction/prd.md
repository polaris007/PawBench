# Fix CLI label-dimension report reading nested task labels

## Background

When running PawBench from the CLI, the printed `Label-Dimension Report` and the
`summary.by_label` block in the results JSON are computed from
`TaskResult.labels`. That dict is populated from the task's YAML front-matter.

The dataset (`data/pawbench-v1.0/tasks/*.md`) stores all taxonomy under a
**nested** `labels:` mapping:

```yaml
labels:
  capabilities: [Tool_Use, Code_Manipulation, Logic_Reasoning]
  complexity: L3
  scenario: Content_Creation/Design
  modality: {type: multimodal, channels: [image]}
  environment: closed
```

All 150/150 tasks have this nested mapping. However, the CLI extracts labels
from the **top-level** front-matter keys (`pawbench/backend.py:438-442` and
`pawbench/runner.py:403-409`). Only a coincidental subset of tasks also carries
dirty top-level duplicates:

- 35/150 tasks have a top-level `complexity`
- 15/150 tasks have a top-level `capabilities`

Only those top-level duplicates reach the report, so the CLI report covers the
wrong, tiny subset. Observed symptom: the screen report shows
`complexity` total 35 / `capabilities` total 83 with very few passes, while the
JSON `summary.passed` (computed over all 150 results) shows 38. The two are not
inconsistent — the label report is bucketing a wrong 35/15-task subset.

The site pipeline already does this correctly: `site/scripts/build_tasks.py:63,84-93`
reads nested `labels` first and only falls back to top-level keys.

## Goal

Make the CLI label extraction read the nested `labels:` mapping first (falling
back to top-level keys for backward compatibility), so the CLI
`Label-Dimension Report` and `summary.by_label` aggregate over all 150 tasks and
agree with the site's slice analysis.

## Requirements

- Extraction must prefer nested `frontmatter["labels"][<key>]` for
  `scenario`, `capabilities`, `complexity`, `modality`, `environment`.
- Fall back to the legacy top-level `frontmatter[<key>]` only when the nested
  key is absent (backward compatibility with any task that still uses flat keys).
- Apply the same extraction in both places that build `TaskResult.labels`:
  - `pawbench/backend.py` (`run_and_grade`, the success path)
  - `pawbench/runner.py` (`_error_result`, the error path)
- Do not change the `labels` schema stored in `TaskResult`/JSON output; only fix
  where it is read from. `_build_label_summary` stays as-is.
- Idempotent/no behavior change for tasks whose nested and top-level values
  agree.

## Acceptance Criteria

- [ ] After the fix, running over the full dataset yields a label report whose
      `complexity` totals sum to 150 and whose `capabilities` rows cover all 150
      tasks (Tool_Use ≈ 149, Planning 91, Logic_Reasoning 89, …), not 35/15.
- [ ] `summary.by_label` in the results JSON matches the printed report and is
      consistent with the site's `tasks.json`-derived stats for the same run.
- [ ] Error/timeout results also carry nested labels (e.g. a task forced to fail
      still appears in its `complexity`/`capabilities` bucket).
- [ ] For the 35 tasks with conflicting top-level duplicates, the nested value
      wins (e.g. `T139_skillsbench_taxonomy-tree-merge` reports 4 capabilities,
      not 6).
- [ ] No regression: `TaskResult.labels` keys/values are unchanged for tasks
      where nested and top-level agree.

## Verification

- Unit-level: call the extraction on a task fixture with nested-only labels,
  nested+top-level conflict, and top-level-only, asserting nested-first order.
- End-to-end smoke: build `TaskResult`s for the 150 tasks and assert
  `_build_label_summary` totals as above.

## Out of Scope

- Cleaning the dirty top-level duplicate fields in the dataset (separate
  data-hygiene task).
- Changing site scripts (they are already correct and serve as the reference).
- Reworking the label report layout or pass/avg-score definitions.

## Notes

- This is a lightweight, PRD-only task.
- Reference implementation to mirror: `site/scripts/build_tasks.py:84-93`.