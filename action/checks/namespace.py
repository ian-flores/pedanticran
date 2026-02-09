"""NAMESPACE checks for CRAN submission readiness.

Implements NS-01 through NS-05 as static analysis checks.
NS-06 and NS-07 require R-level analysis and are knowledge-base only.
"""

import re
from pathlib import Path

# Import Finding from parent check module — when used as part of the action,
# this module is imported by check.py which provides the Finding class.
# For standalone use, define it here.
try:
    from action.check import Finding
except ImportError:
    try:
        from check import Finding
    except ImportError:
        from dataclasses import dataclass

        @dataclass
        class Finding:
            rule_id: str
            severity: str
            title: str
            message: str
            file: str = ""
            line: int = 0
            cran_says: str = ""


# Known S3 generics for NS-03 detection
KNOWN_S3_GENERICS = {
    "print", "summary", "format", "plot", "str", "as.data.frame",
    "as.list", "as.character", "as.numeric", "as.integer", "as.logical",
    "as.double", "as.complex", "as.vector", "as.matrix", "as.array",
    "c", "t", "dim", "dimnames", "length", "names", "levels",
    "merge", "subset", "transform", "within", "with",
    "Math", "Ops", "Summary", "Complex",
    "predict", "residuals", "fitted", "coef", "confint", "vcov",
    "logLik", "AIC", "BIC", "deviance", "nobs",
    "update", "anova", "model.matrix", "model.frame",
    "head", "tail", "rev", "sort", "order", "unique", "duplicated",
    "cbind", "rbind", "rep", "seq", "range", "diff", "cumsum",
    "mean", "median", "quantile", "var", "sd",
    "is.na", "is.finite", "is.infinite", "is.nan",
    "toString", "toJSON", "knit_print",
}

# Broad export patterns that are too permissive
BROAD_EXPORT_PATTERNS = [
    r'^\^?\[?\[?:alpha:\]',        # ^[[:alpha:]]
    r'^\\.',                         # . (matches everything)
    r'^\.$',                         # literal .
    r'^\^?\[?\^\\?\.\]',           # ^[^\\.]  or ^[^.]
    r'^\^?\[?\[:alpha:\]\]',       # [[:alpha:]]
]


def parse_namespace(path: Path) -> dict:
    """Parse NAMESPACE file into structured data.

    Returns dict with keys:
        imports: list of (package,) tuples for import() directives
        import_from: list of (package, function, line_num) tuples
        exports: list of (function, line_num) tuples
        export_patterns: list of (pattern, line_num) tuples
        s3methods: list of (generic, class, line_num) tuples
        raw_lines: list of all lines
    """
    ns_file = path / "NAMESPACE"
    result = {
        "imports": [],
        "import_from": [],
        "exports": [],
        "export_patterns": [],
        "s3methods": [],
        "raw_lines": [],
    }

    if not ns_file.exists():
        return result

    try:
        text = ns_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return result

    result["raw_lines"] = text.splitlines()

    # Join continuation lines (lines ending with comma or opening paren
    # that continue on next line)
    joined = _join_continuation_lines(text)

    for line_num, line in joined:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # import(pkg) or import(pkg, except=c(...))
        m = re.match(r'import\s*\(\s*([^,)]+)', line)
        if m and not line.startswith("importFrom"):
            pkg = m.group(1).strip().strip('"').strip("'")
            result["imports"].append((pkg, line_num))
            continue

        # importFrom(pkg, fun1, fun2, ...)
        m = re.match(r'importFrom\s*\((.+)\)', line)
        if m:
            args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
            if len(args) >= 2:
                pkg = args[0]
                for fun in args[1:]:
                    fun = fun.strip()
                    if fun:
                        result["import_from"].append((pkg, fun, line_num))
            continue

        # export(fun1, fun2, ...)
        m = re.match(r'export\s*\((.+)\)', line)
        if m and not line.startswith("exportPattern"):
            funs = [f.strip().strip('"').strip("'") for f in m.group(1).split(",")]
            for fun in funs:
                if fun:
                    result["exports"].append((fun, line_num))
            continue

        # exportPattern(regex)
        m = re.match(r'exportPattern\s*\(\s*"([^"]*)"\s*\)', line)
        if not m:
            m = re.match(r"exportPattern\s*\(\s*'([^']*)'\s*\)", line)
        if m:
            result["export_patterns"].append((m.group(1), line_num))
            continue

        # S3method(generic, class) or S3method(generic, class, method)
        m = re.match(r'S3method\s*\((.+)\)', line)
        if m:
            args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
            if len(args) >= 2:
                result["s3methods"].append((args[0], args[1], line_num))
            continue

    return result


def _join_continuation_lines(text: str) -> list[tuple[int, str]]:
    """Join multi-line NAMESPACE directives into single logical lines.

    Returns list of (line_number, joined_line) where line_number is the
    starting line of the directive.
    """
    lines = text.splitlines()
    result = []
    current = ""
    start_line = 0
    paren_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if paren_depth == 0:
                result.append((i + 1, stripped))
                continue

        if paren_depth == 0:
            current = stripped
            start_line = i + 1
        else:
            current += " " + stripped

        paren_depth += stripped.count("(") - stripped.count(")")

        if paren_depth <= 0:
            result.append((start_line, current))
            current = ""
            paren_depth = 0

    # Handle unterminated directive
    if current:
        result.append((start_line, current))

    return result


def parse_description_depends(desc: dict) -> list[str]:
    """Extract package names from the Depends field of DESCRIPTION."""
    depends_str = desc.get("Depends", "")
    if not depends_str:
        return []

    packages = []
    for item in depends_str.split(","):
        item = item.strip()
        # Remove version constraints like (>= 3.5.0)
        pkg_name = re.sub(r'\s*\(.*\)', '', item).strip()
        if pkg_name:
            packages.append(pkg_name)
    return packages


def check_namespace(path: Path, desc: dict) -> list[Finding]:
    """Check NAMESPACE for CRAN policy violations.

    Implements NS-01 through NS-05.
    """
    findings = []
    ns_file = path / "NAMESPACE"

    if not ns_file.exists():
        return findings

    ns_rel = str(ns_file.relative_to(path)) if path != ns_file.parent else "NAMESPACE"
    ns = parse_namespace(path)

    # NS-01: Import conflicts — duplicate importFrom targets
    _check_import_conflicts(ns, ns_rel, findings)

    # NS-02: Prefer importFrom over import
    _check_prefer_import_from(ns, ns_rel, findings)

    # NS-03: S3 method exported but not registered
    _check_s3_registration(ns, ns_rel, findings)

    # NS-04: Broad exportPattern
    _check_broad_export_pattern(ns, ns_rel, findings)

    # NS-05: Depends vs Imports misuse
    _check_depends_misuse(ns, desc, path, findings)

    return findings


def _check_import_conflicts(ns: dict, ns_rel: str, findings: list[Finding]):
    """NS-01: Detect duplicate importFrom targets from different packages."""
    # Group importFrom by function name
    func_sources: dict[str, list[tuple[str, int]]] = {}
    for pkg, fun, line_num in ns["import_from"]:
        if fun not in func_sources:
            func_sources[fun] = []
        func_sources[fun].append((pkg, line_num))

    for fun, sources in func_sources.items():
        pkgs = [s[0] for s in sources]
        unique_pkgs = set(pkgs)
        if len(unique_pkgs) > 1:
            line = sources[0][1]
            pkg_list = ", ".join(sorted(unique_pkgs))
            findings.append(Finding(
                rule_id="NS-01",
                severity="warning",
                title=f"Import conflict: '{fun}' imported from multiple packages",
                message=f"Function '{fun}' is imported from: {pkg_list}. "
                        f"This causes 'Replacing previous import' warnings.",
                file=ns_rel,
                line=line,
                cran_says="Replacing previous import by another import.",
            ))

    # Also flag multiple import() directives as high collision risk
    if len(ns["imports"]) > 1:
        pkgs = [i[0] for i in ns["imports"]]
        line = ns["imports"][0][1]
        findings.append(Finding(
            rule_id="NS-01",
            severity="warning",
            title="Multiple full namespace imports risk collisions",
            message=f"import() used for multiple packages: {', '.join(pkgs)}. "
                    f"Functions with the same name will collide silently.",
            file=ns_rel,
            line=line,
            cran_says="Replacing previous import by another import.",
        ))


def _check_prefer_import_from(ns: dict, ns_rel: str, findings: list[Finding]):
    """NS-02: Flag import() directives (prefer importFrom)."""
    # Packages where import() is commonly accepted
    accepted_full_import = {"methods"}

    for pkg, line_num in ns["imports"]:
        if pkg.lower() in {p.lower() for p in accepted_full_import}:
            continue
        findings.append(Finding(
            rule_id="NS-02",
            severity="note",
            title=f"Full namespace import of '{pkg}'",
            message=f"import({pkg}) imports the entire namespace. "
                    f"Prefer importFrom({pkg}, fun1, fun2, ...) for selective imports.",
            file=ns_rel,
            line=line_num,
            cran_says="Using importFrom selectively rather than import is good practice.",
        ))


def _check_s3_registration(ns: dict, ns_rel: str, findings: list[Finding]):
    """NS-03: Flag S3 methods exported via export() instead of S3method()."""
    # Build set of registered S3 methods
    registered = set()
    for generic, cls, _ in ns["s3methods"]:
        registered.add(f"{generic}.{cls}")

    for fun, line_num in ns["exports"]:
        if "." not in fun:
            continue

        # Try to split as generic.class
        # Check each possible split point (first dot, since generics
        # like as.data.frame have dots too)
        parts = fun.split(".", 1)
        generic_candidate = parts[0]
        class_candidate = parts[1] if len(parts) > 1 else ""

        if not class_candidate:
            continue

        # Check if the generic part is a known S3 generic
        if generic_candidate in KNOWN_S3_GENERICS:
            if fun not in registered:
                findings.append(Finding(
                    rule_id="NS-03",
                    severity="note",
                    title=f"S3 method '{fun}' exported but not registered",
                    message=f"'{fun}' looks like an S3 method for generic '{generic_candidate}'. "
                            f"Use S3method({generic_candidate}, {class_candidate}) instead of export({fun}).",
                    file=ns_rel,
                    line=line_num,
                    cran_says="Found the following apparent S3 methods exported but not registered.",
                ))


def _check_broad_export_pattern(ns: dict, ns_rel: str, findings: list[Finding]):
    """NS-04: Flag overly broad exportPattern directives."""
    for pattern, line_num in ns["export_patterns"]:
        is_broad = False

        # Check known broad patterns
        if pattern in (".", "^[[:alpha:]]", "^[^\\.]", "^[^.]",
                       "^[[:alpha:]]+", "^[[:alpha:]].*"):
            is_broad = True

        # Check if pattern is a single character class that matches most names
        if re.match(r'^\^?\[', pattern) and len(pattern) < 20:
            # Likely a broad character class pattern
            if "alpha" in pattern or ("^" in pattern and "." in pattern):
                is_broad = True

        if is_broad:
            findings.append(Finding(
                rule_id="NS-04",
                severity="note",
                title=f"Broad exportPattern: '{pattern}'",
                message=f"exportPattern(\"{pattern}\") exports most/all functions including internals. "
                        f"Use explicit export() directives for each public function instead.",
                file=ns_rel,
                line=line_num,
                cran_says="Exporting all functions with exportPattern is strongly discouraged.",
            ))


def _check_depends_misuse(ns: dict, desc: dict, path: Path,
                           findings: list[Finding]):
    """NS-05: Flag packages in Depends that should be in Imports."""
    depends_pkgs = parse_description_depends(desc)
    desc_file = str((path / "DESCRIPTION").relative_to(path)) if path != (path / "DESCRIPTION").parent else "DESCRIPTION"

    # Packages that are acceptable in Depends
    accepted_depends = {"R", "methods"}

    # Build set of packages imported in NAMESPACE
    ns_imported = set()
    for pkg, _ in ns["imports"]:
        ns_imported.add(pkg)
    for pkg, _, _ in ns["import_from"]:
        ns_imported.add(pkg)

    for pkg in depends_pkgs:
        if pkg in accepted_depends:
            continue

        message = (
            f"Package '{pkg}' is in Depends but should likely be in Imports. "
            f"Depends loads the package onto the user's search path."
        )

        # Extra note if package is not even imported in NAMESPACE
        if pkg not in ns_imported:
            message += (
                f" '{pkg}' is not imported in NAMESPACE either, "
                f"which may cause 'no visible binding' NOTEs."
            )

        findings.append(Finding(
            rule_id="NS-05",
            severity="note",
            title=f"'{pkg}' in Depends instead of Imports",
            message=message,
            file=desc_file,
            cran_says="The Depends field should nowadays be used rarely.",
        ))
