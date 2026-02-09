"""Vignette checks for CRAN submission readiness.

Implements VIG-01 through VIG-05:
  VIG-01: VignetteBuilder not declared in DESCRIPTION
  VIG-02: Missing VignetteEngine/VignetteIndexEntry/VignetteEncoding metadata
  VIG-03: Stale pre-built vignettes in inst/doc
  VIG-04: Vignette build dependencies not declared
  VIG-05: HTML vignette size — html_document vs html_vignette
"""

import re
from pathlib import Path

# Import shared types from parent — when integrated into check.py these will be local
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from check import Finding, scan_file


def find_vignette_files(path: Path) -> list[Path]:
    """Find all vignette source files in vignettes/ directory."""
    vig_dir = path / "vignettes"
    if not vig_dir.is_dir():
        return []
    files = []
    for ext in ("*.Rmd", "*.Rnw", "*.qmd"):
        files.extend(vig_dir.glob(ext))
    return sorted(files)


def parse_vignette_metadata(filepath: Path) -> dict:
    """Extract %\\Vignette* metadata from a vignette file.

    Returns dict with keys: engine, index_entry, encoding, depends.
    Each value is (line_number, value_string) or None if not found.
    """
    metadata = {"engine": None, "index_entry": None, "encoding": None, "depends": None}
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return metadata

    for i, line in enumerate(text.splitlines(), 1):
        m = re.search(r'%\\VignetteEngine\{([^}]+)\}', line)
        if m:
            metadata["engine"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteIndexEntry\{([^}]+)\}', line)
        if m:
            metadata["index_entry"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteEncoding\{([^}]+)\}', line)
        if m:
            metadata["encoding"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteDepends\{([^}]+)\}', line)
        if m:
            metadata["depends"] = (i, m.group(1).strip())

    return metadata


def extract_packages_from_vignette(filepath: Path) -> set[str]:
    """Extract package names used in vignette R code chunks.

    Looks for library(pkg), require(pkg), pkg::func() patterns
    inside R code chunks (between ```{r ...} and ```).
    """
    packages = set()
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return packages

    in_chunk = False
    for line in text.splitlines():
        # Detect R code chunk boundaries (Rmd style)
        if re.match(r'^```\{r', line):
            in_chunk = True
            continue
        if in_chunk and line.strip().startswith('```'):
            in_chunk = False
            continue

        if in_chunk:
            # library(pkg) or require(pkg)
            for m in re.finditer(r'\b(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', line):
                packages.add(m.group(1))
            # pkg::func() or pkg:::func()
            for m in re.finditer(r'\b(\w+):::\w+|\b(\w+)::\w+', line):
                pkg = m.group(1) or m.group(2)
                packages.add(pkg)

    # For .Rnw files, look for code between <<...>>= and @
    if filepath.suffix.lower() == '.rnw':
        in_chunk = False
        for line in text.splitlines():
            if re.match(r'^<<.*>>=', line):
                in_chunk = True
                continue
            if in_chunk and line.strip() == '@':
                in_chunk = False
                continue
            if in_chunk:
                for m in re.finditer(r'\b(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', line):
                    packages.add(m.group(1))
                for m in re.finditer(r'\b(\w+):::\w+|\b(\w+)::\w+', line):
                    pkg = m.group(1) or m.group(2)
                    packages.add(pkg)

    return packages


def parse_desc_packages(desc: dict) -> set[str]:
    """Extract all declared package names from DESCRIPTION Imports + Suggests + Depends."""
    packages = set()
    for field in ("Imports", "Suggests", "Depends"):
        raw = desc.get(field, "")
        if raw:
            for entry in raw.split(","):
                # Strip version constraints: "pkg (>= 1.0)" -> "pkg"
                pkg = entry.strip().split("(")[0].strip()
                if pkg and pkg != "R":
                    packages.add(pkg)
    return packages


def get_vignette_output_format(filepath: Path) -> list[tuple[int, str]]:
    """Check vignette YAML for output format declarations.

    Returns list of (line_number, format_string) found.
    """
    formats = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return formats

    in_yaml = False
    for i, line in enumerate(text.splitlines(), 1):
        if i == 1 and line.strip() == '---':
            in_yaml = True
            continue
        if in_yaml and line.strip() == '---':
            break
        if in_yaml:
            m = re.match(r'\s*output\s*:\s*(\S+)', line)
            if m:
                formats.append((i, m.group(1)))
            # Also catch indented format like:
            #   output:
            #     html_document:
            m = re.match(r'\s+(html_document|rmarkdown::html_document)\s*:', line)
            if m and not formats:
                formats.append((i, m.group(1)))

    return formats


def check_vignettes(path: Path, desc: dict) -> list[Finding]:
    """Check vignette configuration and metadata."""
    findings = []
    vig_dir = path / "vignettes"
    vig_files = find_vignette_files(path)

    if not vig_files:
        return findings

    # --- VIG-01: VignetteBuilder not declared ---
    vb_raw = desc.get("VignetteBuilder", "")
    vb_list = [x.strip().lower() for x in vb_raw.split(",") if x.strip()] if vb_raw else []

    if not vb_raw:
        # Vignettes exist but no VignetteBuilder declared
        # Only flag if vignettes use a non-Sweave engine (Sweave is built-in)
        has_non_sweave = False
        for vf in vig_files:
            if vf.suffix.lower() in ('.rmd', '.qmd'):
                has_non_sweave = True
                break
            meta = parse_vignette_metadata(vf)
            if meta["engine"] and "sweave" not in meta["engine"][1].lower():
                has_non_sweave = True
                break

        if has_non_sweave:
            findings.append(Finding(
                rule_id="VIG-01", severity="error",
                title="VignetteBuilder not declared in DESCRIPTION",
                message="Package has vignettes using a non-Sweave engine but no VignetteBuilder field. "
                        "Add VignetteBuilder: knitr to DESCRIPTION and knitr to Suggests.",
                file=str(path / "DESCRIPTION"),
                cran_says="Package has 'vignettes' subdirectory but apparently no vignettes. "
                          "Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"
            ))
    else:
        # Check that knitr vignettes also have rmarkdown declared
        for vf in vig_files:
            meta = parse_vignette_metadata(vf)
            if meta["engine"]:
                engine_val = meta["engine"][1]
                if "knitr::rmarkdown" in engine_val:
                    # Both knitr and rmarkdown should be in VignetteBuilder or at least Suggests
                    declared_pkgs = parse_desc_packages(desc)
                    if "rmarkdown" not in declared_pkgs and "rmarkdown" not in vb_list:
                        findings.append(Finding(
                            rule_id="VIG-01", severity="error",
                            title="rmarkdown not declared for knitr::rmarkdown vignettes",
                            message=f"Vignette '{vf.name}' uses knitr::rmarkdown engine but "
                                    "rmarkdown is not in Suggests or VignetteBuilder.",
                            file=str(vf.relative_to(path)),
                            line=meta["engine"][0],
                            cran_says="Package has 'vignettes' subdirectory but apparently no vignettes."
                        ))
                        break  # One finding is enough

    # --- VIG-02: Missing metadata per vignette ---
    placeholder_titles = {"vignette title", "vignette-title", "untitled"}

    for vf in vig_files:
        rel = str(vf.relative_to(path))
        meta = parse_vignette_metadata(vf)

        # Missing VignetteEngine
        if not meta["engine"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="error",
                title=f"Missing %\\VignetteEngine in {vf.name}",
                message="Every vignette must declare its processing engine. "
                        "Add %\\VignetteEngine{knitr::rmarkdown} to the YAML frontmatter.",
                file=rel,
                cran_says="Files named as vignettes but with no recognized vignette engine."
            ))

        # Missing VignetteIndexEntry
        if not meta["index_entry"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="error",
                title=f"Missing %\\VignetteIndexEntry in {vf.name}",
                message="Every vignette must declare its title for the vignette index. "
                        "Add %\\VignetteIndexEntry{Your Descriptive Title} to the YAML frontmatter.",
                file=rel,
            ))
        elif meta["index_entry"][1].lower().strip() in placeholder_titles:
            findings.append(Finding(
                rule_id="VIG-02", severity="warning",
                title=f"Placeholder VignetteIndexEntry in {vf.name}",
                message=f"VignetteIndexEntry is '{meta['index_entry'][1]}' which is a placeholder. "
                        "Replace with a descriptive title.",
                file=rel, line=meta["index_entry"][0],
                cran_says="Vignette with placeholder title 'Vignette Title'."
            ))

        # Missing VignetteEncoding
        if not meta["encoding"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="note",
                title=f"Missing %\\VignetteEncoding in {vf.name}",
                message="Add %\\VignetteEncoding{UTF-8} to the YAML frontmatter.",
                file=rel,
            ))
        elif meta["encoding"][1] != "UTF-8":
            findings.append(Finding(
                rule_id="VIG-02", severity="note",
                title=f"Non-UTF-8 VignetteEncoding in {vf.name}",
                message=f"VignetteEncoding is '{meta['encoding'][1]}'. CRAN expects UTF-8.",
                file=rel, line=meta["encoding"][0],
            ))

    # --- VIG-03: Stale pre-built vignettes in inst/doc ---
    inst_doc = path / "inst" / "doc"
    if inst_doc.is_dir():
        inst_doc_files = {f.stem: f for f in inst_doc.iterdir() if f.suffix.lower() in ('.html', '.pdf')}
        vig_sources = {f.stem: f for f in vig_files}

        # Check for vignette sources without corresponding output
        for stem, src_file in vig_sources.items():
            if stem not in inst_doc_files:
                findings.append(Finding(
                    rule_id="VIG-03", severity="warning",
                    title=f"Vignette source without pre-built output: {src_file.name}",
                    message=f"'{src_file.name}' exists in vignettes/ but no matching .html/.pdf in inst/doc/. "
                            "Either remove inst/doc/ or rebuild.",
                    file=str(src_file.relative_to(path)),
                    cran_says="Files in 'vignettes' but not in 'inst/doc'."
                ))

        # Check for orphaned outputs (output with no source)
        for stem, out_file in inst_doc_files.items():
            if stem not in vig_sources:
                findings.append(Finding(
                    rule_id="VIG-03", severity="warning",
                    title=f"Orphaned pre-built vignette: {out_file.name}",
                    message=f"'{out_file.name}' in inst/doc/ has no matching source in vignettes/. "
                            "Remove orphaned output files.",
                    file=str(out_file.relative_to(path)),
                ))

        # Check timestamps: source newer than output
        for stem in vig_sources:
            if stem in inst_doc_files:
                src_mtime = vig_sources[stem].stat().st_mtime
                out_mtime = inst_doc_files[stem].stat().st_mtime
                if src_mtime > out_mtime:
                    findings.append(Finding(
                        rule_id="VIG-03", severity="warning",
                        title=f"Stale pre-built vignette: {inst_doc_files[stem].name}",
                        message=f"Source '{vig_sources[stem].name}' is newer than pre-built "
                                f"'{inst_doc_files[stem].name}'. Rebuild vignettes.",
                        file=str(inst_doc_files[stem].relative_to(path)),
                    ))

        # Check if inst/doc is in .gitignore
        gitignore = path / ".gitignore"
        if gitignore.exists():
            gi_text = gitignore.read_text(encoding="utf-8", errors="replace")
            if "inst/doc" not in gi_text:
                findings.append(Finding(
                    rule_id="VIG-03", severity="note",
                    title="inst/doc/ not in .gitignore",
                    message="Best practice: add inst/doc to .gitignore. "
                            "usethis::use_vignette() does this by default.",
                    file=".gitignore",
                ))

    # --- VIG-04: Vignette build dependencies not declared ---
    declared_pkgs = parse_desc_packages(desc)
    # The package itself is always available
    pkg_name = desc.get("Package", "")
    if pkg_name:
        declared_pkgs.add(pkg_name)
    # Base R packages are always available
    base_pkgs = {"base", "utils", "stats", "methods", "grDevices", "graphics",
                 "tools", "compiler", "datasets", "grid", "parallel", "splines",
                 "stats4", "tcltk"}
    declared_pkgs.update(base_pkgs)

    for vf in vig_files:
        used_pkgs = extract_packages_from_vignette(vf)
        undeclared = used_pkgs - declared_pkgs
        if undeclared:
            rel = str(vf.relative_to(path))
            findings.append(Finding(
                rule_id="VIG-04", severity="error",
                title=f"Undeclared vignette dependencies in {vf.name}",
                message=f"Packages used in vignette but not in DESCRIPTION: {', '.join(sorted(undeclared))}. "
                        "Add them to Suggests.",
                file=rel,
                cran_says="Package suggested but not available."
            ))

    # --- VIG-05: HTML vignette size ---
    for vf in vig_files:
        if vf.suffix.lower() not in ('.rmd', '.qmd'):
            continue

        rel = str(vf.relative_to(path))
        output_formats = get_vignette_output_format(vf)

        for line_num, fmt in output_formats:
            if fmt in ("html_document", "rmarkdown::html_document"):
                findings.append(Finding(
                    rule_id="VIG-05", severity="note",
                    title=f"html_document output in {vf.name}",
                    message="Using html_document instead of html_vignette adds ~600KB of Bootstrap/jQuery. "
                            "Switch to rmarkdown::html_vignette to reduce size.",
                    file=rel, line=line_num,
                    cran_says="Installed size is too large."
                ))

    # Check inst/doc HTML file sizes
    if inst_doc.is_dir():
        for html_file in inst_doc.glob("*.html"):
            size_mb = html_file.stat().st_size / (1024 * 1024)
            if size_mb > 1.0:
                findings.append(Finding(
                    rule_id="VIG-05", severity="warning",
                    title=f"Large HTML vignette: {html_file.name} ({size_mb:.1f}MB)",
                    message="HTML vignette exceeds 1MB. Use html_vignette output, lower DPI, "
                            "and compress images to reduce size.",
                    file=str(html_file.relative_to(path)),
                    cran_says="Installed size is too large."
                ))

    return findings
