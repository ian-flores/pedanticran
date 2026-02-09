# pedanticran

> **Warning**
> This project is experimental. Rules may be incomplete, checks may have false positives, and the API may change without notice. Use it as a supplement to — not a replacement for — reading the [CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html) yourself.

**pedanticran** catches the policy violations that `R CMD check` misses — the ones that get your package rejected with a terse two-line email. It encodes 79 CRAN rules (compiled from 3 years of mailing list rejections) with verbatim rejection text, so you can fix issues before a human reviewer finds them.

Works as a **Claude Code plugin** (interactive) or a **GitHub Action** (CI).

## The problem

[~35% of first-time CRAN submissions](https://llrs.dev/post/2024/01/10/submission-cran-first-try/) are rejected for policy issues, not code issues. Things like:

- `T` instead of `TRUE`
- Title not in Title Case (but "a" should be lowercase, and don't capitalize after a colon if...)
- `print()` where you should use `message()`
- Missing `\value` tag on one exported function out of forty
- `\dontrun{}` where CRAN wanted `\donttest{}`
- `bool` redefined in C code (now a keyword in C23/R 4.5+)
- Lost braces in Rd files (broke 3,000+ packages in R 4.4)
- Date field that's a month old blocking your resubmission

`R CMD check` doesn't catch these. pedanticran does.

## Quick start

### GitHub Action

Add to `.github/workflows/cran-check.yml`:

```yaml
name: CRAN Policy Check
on: [push, pull_request]

jobs:
  pedantic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ian-flores/pedanticran@main
        with:
          severity: 'warning'
          fail-on: 'error'
```

No R installation required. Runs in seconds. Annotates the exact files and lines.

### Claude Code plugin

```bash
# Install globally (available in all projects)
curl -fsSL https://raw.githubusercontent.com/ian-flores/pedanticran/main/install.sh | bash -s -- --global

# Or install locally in your R package
curl -fsSL https://raw.githubusercontent.com/ian-flores/pedanticran/main/install.sh | bash -s -- --local
```

Then in Claude Code, inside your R package directory:

| Command | What it does |
|---------|-------------|
| `/cran-audit` | Read-only audit. Finds issues, grouped by severity. |
| `/cran-fix` | Fixes what it can. Asks before touching anything risky. |
| `/cran-respond` | Paste a CRAN rejection email. Gets a fix plan + resubmission draft. |

## What it checks

79 rules across 12 categories, sourced from 3 years (2023–2025) of CRAN mailing list rejections and policy revisions:

| Category | Rules | Examples |
|----------|------:|---------|
| DESCRIPTION | 15 | Title case, quoting software names, valid Authors@R, license format, stale Date field, smart quotes |
| Code Behavior | 18 | T/F literals, print→message, options/par without on.exit, seed in functions, browser() calls, sprintf deprecation |
| Compiled Code | 9 | C23 keywords, R_NO_REMAP, non-API entry points, strict prototypes, Fortran KIND, Rust vendoring |
| Documentation | 9 | Missing @return, \dontrun misuse, lost braces (R 4.3+), HTML5 Rd validation |
| Licensing | 3 | License validity, license changes, dual licensing prohibition |
| Size & Performance | 2 | Tarball size (10MB), check time (10 min) |
| Cross-Platform | 2 | Multi-platform support, no binary executables |
| Dependencies | 3 | Strong deps on CRAN, conditional Suggests, dependency health monitoring |
| Internet | 3 | Graceful failure, HTTPS, rate limit policy (rev6277) |
| Submission | 7 | R CMD check, multi-platform testing, reverse deps, vacation periods |
| Package Naming | 2 | Case-insensitive uniqueness, permanence |
| Miscellaneous | 6 | NEWS format, URL validity, spelling, .Rbuildignore, Makefile portability |

Every rule includes the verbatim CRAN rejection text, so you know exactly what reviewers will say.

## GitHub Action options

```yaml
- uses: ian-flores/pedanticran@main
  with:
    path: '.'          # Path to R package (default: repo root)
    severity: 'warning' # Minimum severity to report: error, warning, note
    fail-on: 'error'    # Fail the check at this severity
```

**Outputs:** `issues`, `errors`, `warnings`, `notes` — use in downstream steps.

The checker is pure Python (stdlib only). No R, no compiled dependencies. Runs 30 static analysis checks covering DESCRIPTION, R code, C/C++/Fortran, Makevars, configure scripts, and documentation.

## How `/cran-fix` works

Fixes are applied in tiers:

1. **Mechanical** (applied automatically): `T`→`TRUE`, `http`→`https`, `\dontrun`→`\donttest`, smart quotes, stale Date field, `sprintf`→`snprintf`, `#!/bin/bash`→`#!/bin/sh`
2. **Safe with review** (shows diff first): Title case, quoting names, adding `@return` tags, `Rf_` prefix for C++ R API, lost braces in Rd, Fortran KIND portability
3. **Needs input** (asks you): License choice, rewriting Description, C23 keyword conflicts, Rust crate vendoring, rate limiting strategy

Nothing destructive happens without your approval.

## How `/cran-respond` works

Paste your rejection email. pedanticran:

1. Parses every distinct issue from the email
2. Maps each to a specific policy rule
3. Scans for related issues CRAN didn't mention yet (if they flagged one missing `@return`, it checks all your exports)
4. Provides exact fixes with file paths
5. Drafts your resubmission comment

## Contributing

The knowledge base (`knowledge/cran-rules.md`) is the heart of the project. If you've been rejected for a reason not covered, open an issue with the rejection text.

## License

MIT
