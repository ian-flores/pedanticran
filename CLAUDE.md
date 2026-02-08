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

## Phase Roadmap

1. **Phase 1** (current): Knowledge base + `/cran-audit` (read-only)
2. **Phase 2**: `/cran-fix` (auto-remediation)
3. **Phase 3**: `/cran-respond` (rejection email parser)
4. **Phase 4**: GitHub Action wrapper
