# pedanticran

[![Tests](https://github.com/ian-flores/pedanticran/actions/workflows/test.yml/badge.svg)](https://github.com/ian-flores/pedanticran/actions/workflows/test.yml)

> **Beta.** Some checks may flag things that are fine. Options may change between versions. Use pedanticran alongside the [CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html), not instead of it.

pedanticran finds the problems that get R packages rejected by CRAN, before you submit.

`R CMD check` tells you if your package builds and runs. It does not tell you if a CRAN reviewer will accept it. Reviewers also check things like how you wrote your title, whether you used `print()` instead of `message()`, and whether every exported function documents what it returns. pedanticran checks those things too.

It knows 155 rules. They come from CRAN's policy, R release notes, and CRAN rejection emails posted to the R mailing lists from 2015 to September 2026. Each rule includes the exact words CRAN reviewers use when they reject a package for it.

You can use it in two ways:

- **In Claude Code**, to audit your package, fix problems, or answer a rejection email.
- **In GitHub Actions**, to check your package on every push.

## Why you might need this

[About 35% of first-time CRAN submissions](https://llrs.dev/post/2024/01/10/submission-cran-first-try/) are rejected. Many are rejected for small policy problems, not broken code. For example:

- Writing `T` instead of `TRUE`
- A title that is not in Title Case
- Using `print()` where CRAN wants `message()`
- One exported function out of forty with no `\value` section
- Using `\dontrun{}` where CRAN wanted `\donttest{}`
- A `Date` field more than a month old
- C code that uses `bool` as a name (it is a keyword in the C23 standard, which R 4.5 uses by default)

`R CMD check` does not catch these. pedanticran does.

## Getting started

### Use it in Claude Code

Run these two commands in Claude Code:

```
/plugin marketplace add ian-flores/pedanticran
/plugin install pedanticran@pedanticran
```

Then open Claude Code in your R package folder and use one of these commands:

| Command | What it does |
|---------|--------------|
| `/pedanticran:cran-audit` | Looks for problems and lists them by how serious they are. Changes nothing. |
| `/pedanticran:cran-fix` | Fixes the problems it safely can. Asks you before anything risky. |
| `/pedanticran:cran-respond` | Paste in a CRAN rejection email. You get a fix for each point and a draft reply. |

If you don't use the plugin system, you can install the commands by hand. They are then called `/cran-audit`, `/cran-fix` and `/cran-respond`.

```bash
git clone https://github.com/ian-flores/pedanticran.git
cd pedanticran
./install.sh --global    # for all your projects

# or, for one package only, run this from inside the package folder:
/path/to/pedanticran/install.sh --local
```

### Use it in GitHub Actions

Create the file `.github/workflows/cran-check.yml` in your package:

```yaml
name: CRAN Policy Check
on: [push, pull_request]

jobs:
  pedantic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: ian-flores/pedanticran@v1
        with:
          severity: 'warning'
          fail-on: 'error'
```

You don't need R installed. It runs in a few seconds and marks each problem on the exact file and line.

## What it checks

155 rules in 19 groups:

| Group | Rules | Examples |
|-------|------:|----------|
| DESCRIPTION file | 17 | Title Case, quoting software names, `Authors@R`, license format, old `Date` field |
| R code | 24 | `T`/`F`, `print()` vs `message()`, restoring `options()` and `par()`, writing only to temp folders, user cache size |
| Compiled code (C, C++, Fortran, Rust) | 15 | New C and C++ standards, R functions you are not allowed to call, missing C++ headers, Rcpp settings |
| Documentation | 15 | Missing return values, `\dontrun` misuse, broken Rd braces, links that don't work |
| Licensing | 3 | Valid licenses, one license for the whole package |
| Size and speed | 2 | Package size (10 MB), check time (10 minutes) |
| Platforms | 4 | Working on every platform, no binary files, macOS paths |
| Dependencies | 3 | Required packages must be on CRAN or Bioconductor |
| Internet | 3 | Failing politely when a website is down, HTTPS, rate limits |
| Submission | 7 | Testing on several platforms, checking packages that depend on yours, CRAN holidays |
| Package name | 2 | Names must be unique, ignoring case |
| Other | 7 | NEWS file, URLs, spelling, `.Rbuildignore`, Makefiles |
| Encoding | 8 | Non-ASCII characters, missing `Encoding` field |
| Vignettes | 8 | Build setup, metadata, old built files |
| NAMESPACE | 9 | Imports, S3 methods, no `library()` calls in package code |
| Data | 9 | Documenting datasets, compression, size limits |
| System requirements | 7 | Declaring outside libraries and programs, C++ standard |
| Maintainer email | 6 | Mailing lists, throwaway addresses, no-reply addresses |
| `inst/` folder | 6 | Hidden files, old `CITATION` format, other people's copyright |

The full list is in [`knowledge/cran-rules.md`](knowledge/cran-rules.md).

### The GitHub Action checks fewer rules

The GitHub Action checks 141 of the 155 rules. The 14 rules added in the September 2026 update are only used by the Claude Code commands for now.

## GitHub Action settings

```yaml
- uses: ian-flores/pedanticran@v1
  with:
    path: '.'            # where your package is (default: the top of the repo)
    severity: 'warning'  # lowest level to show: error, warning or note
    fail-on: 'error'     # fail the run at this level or above
    online: 'true'       # also check URLs, spelling, and that dependencies exist on CRAN
```

The action reports how many problems it found as `issues`, `errors`, `warnings` and `notes`. Later steps in your workflow can use these numbers.

It is written in plain Python with no extra packages, so it needs no setup.

## How `/cran-fix` works

It sorts fixes into three groups:

1. **Simple fixes it makes on its own**, such as `T` to `TRUE`, `http` to `https`, and removing an old `Date` field.
2. **Fixes it makes and then shows you**, such as Title Case, adding `@return` tags, and fixing Rd braces.
3. **Fixes it asks you about first**, such as choosing a license, rewriting your Description, or limiting how often your package calls a website.

It never deletes or rewrites anything important without asking.

## How `/cran-respond` works

Paste in your rejection email. pedanticran will:

1. Split the email into separate problems.
2. Match each problem to a rule.
3. Look for related problems CRAN didn't mention yet. For example, if CRAN flagged one missing `@return`, it checks every exported function.
4. Tell you exactly what to change, and in which file.
5. Write a draft of your reply to CRAN.

## How it fits with other tools

pedanticran does not replace `R CMD check`. Run both.

| Tool | The question it answers |
|------|-------------------------|
| `R CMD check` | Does the package build and pass R's own checks? |
| `devtools::check()` | The same as `R CMD check`, with an easier way to run it. |
| `devtools::release()` | Did you remember the steps on a release checklist? |
| `goodpractice` | Are there common style problems? (It covers about 10–15% of pedanticran's extra rules.) |
| **pedanticran** | **Will a CRAN reviewer accept this package?** |

There is a detailed comparison in [`research/devtools-comparison.md`](research/devtools-comparison.md).

## Contributing

The rules in [`knowledge/cran-rules.md`](knowledge/cran-rules.md) are the core of this project. If CRAN rejected your package for a reason pedanticran doesn't cover, please open an issue and paste the rejection text.

## License

MIT
