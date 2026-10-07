# Pedantic CRAN

A Claude Code plugin that helps R package developers survive CRAN submission.

## Project Structure

- `knowledge/cran-rules.md` — 155 rules across 19 categories (check.py implements 154; CODE-23 is manual review only), with verbatim rejection text
- `skills/cran-audit/SKILL.md` — The `/cran-audit` skill: reads an R package and produces a pre-submission report
- `skills/cran-fix/SKILL.md` — The `/cran-fix` skill: tiered auto-remediation (mechanical → reviewed → user input)
- `skills/cran-respond/SKILL.md` — The `/cran-respond` skill: parses CRAN rejection emails and drafts resubmission
- `action/check.py` — Python static analyzer covering 154 of the 155 rules (no R dependency)
- `action.yml` — GitHub Action definition (at the repo root so `uses: ian-flores/pedanticran@v1` resolves)
- `.claude-plugin/` — plugin manifest and single-plugin marketplace; bump `version` in both on release
- `tests/` — 331 pytest tests with 3 fixture R packages (clean, problematic, edge-cases)
- `research/` — Mailing list and policy analysis reports (2015 through September 2026) and checker validation
- `install.sh` — Manual install (non-plugin) into `~/.claude/skills/<name>/SKILL.md`

## Development

When editing skills, test them by running the skill on a real R package directory.

When editing `action/check.py`, run the test suite: `python3 -m pytest tests/ -v`

The knowledge base (`knowledge/cran-rules.md`) is the core IP. Keep it:
- Structured by category (DESCRIPTION, code, docs, etc.)
- Each rule has: ID, severity, what CRAN says (verbatim), how to detect, how to fix, since when
- Updated when CRAN policies change

## GitHub Action

The root `action.yml` runs `action/check.py` as a standalone GitHub Action. Users add it to their R package CI:

```yaml
- uses: ian-flores/pedanticran@v1
  with:
    path: '.'
    severity: 'warning'   # report warnings and errors
    fail-on: 'error'      # fail CI only on blocking issues
```

The Python checker (`action/check.py`) encodes knowledge base rules as static analysis.
It runs without R and produces GitHub Actions annotations on the exact files/lines.

## Current State

All four phases are implemented:

1. Knowledge base + `/cran-audit` (read-only)
2. `/cran-fix` (auto-remediation)
3. `/cran-respond` (rejection email parser)
4. GitHub Action (CI integration)

Knowledge base sourced from CRAN mailing list rejections and policy changes, 2015 through September 2026.
Validated against dplyr (large) and glosario (small) — see `research/checker-validation.md`.
CI runs 331 pytest tests on Python 3.11/3.12, plus a job that runs the action itself, via `.github/workflows/test.yml`.
