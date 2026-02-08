# Pedantic CRAN

A Claude Code plugin that helps R package developers survive CRAN submission.

## Project Structure

- `knowledge/cran-rules.md` — Structured knowledge base of all CRAN requirements, with verbatim rejection text
- `skills/cran-audit.md` — The `/cran-audit` skill: reads an R package and produces a pre-submission report
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
- uses: pedanticran/pedanticran@main
  with:
    path: '.'
    severity: 'warning'   # report warnings and errors
    fail-on: 'error'      # fail CI only on blocking issues
```

The Python checker (`action/check.py`) encodes knowledge base rules as static analysis.
It runs without R and produces GitHub Actions annotations on the exact files/lines.

## Phases

1. Knowledge base + `/cran-audit` (read-only)
2. `/cran-fix` (auto-remediation)
3. `/cran-respond` (rejection email parser)
4. GitHub Action (CI integration)
