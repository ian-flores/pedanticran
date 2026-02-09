# Pedantic CRAN

A Claude Code plugin that helps R package developers survive CRAN submission.

## Project Structure

- `knowledge/cran-rules.md` — 130 rules across 19 categories, with verbatim rejection text
- `skills/cran-audit.md` — The `/cran-audit` skill: reads an R package and produces a pre-submission report
- `skills/cran-fix.md` — The `/cran-fix` skill: tiered auto-remediation (mechanical → reviewed → user input)
- `skills/cran-respond.md` — The `/cran-respond` skill: parses CRAN rejection emails and drafts resubmission
- `action/check.py` — Python static analyzer (65+ checks, no R dependency)
- `action/action.yml` — GitHub Action definition
- `research/` — Mailing list analysis reports (2023–2025) and checker validation
- `install.sh` — Installs skills into `~/.claude/skills/`

## Development

When editing skills, test them by running the skill on a real R package directory.

The knowledge base (`knowledge/cran-rules.md`) is the core IP. Keep it:
- Structured by category (DESCRIPTION, code, docs, etc.)
- Each rule has: ID, severity, what CRAN says (verbatim), how to detect, how to fix
- Updated when CRAN policies change

## GitHub Action

The `action/` directory contains a standalone GitHub Action. Users add it to their R package CI:

```yaml
- uses: ian-flores/pedanticran@main
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

Knowledge base sourced from 3 years of CRAN mailing list rejections (2023–2025).
Validated against dplyr (large) and glosario (small) — see `research/checker-validation.md`.
