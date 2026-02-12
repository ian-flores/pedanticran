"""Comprehensive tests for pedanticran's check.py static analyzer.

Tests are organized into:
1. Unit tests for individual functions and data structures
2. Integration tests against fixture packages
3. False-positive filtering tests
4. Output format and CLI tests
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Import the checker module (conftest.py sets up sys.path)
ACTION_DIR = Path(__file__).parent.parent / "action"
sys.path.insert(0, str(ACTION_DIR))

import check

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CHECK_PY = ACTION_DIR / "check.py"


# ============================================================================
# Unit Tests: Finding dataclass
# ============================================================================


class TestFinding:
    """Tests for the Finding dataclass."""

    def test_finding_creation(self):
        f = check.Finding(
            rule_id="CODE-01",
            severity="error",
            title="T/F instead of TRUE/FALSE",
            message="Use TRUE/FALSE, not T/F",
        )
        assert f.rule_id == "CODE-01"
        assert f.severity == "error"
        assert f.title == "T/F instead of TRUE/FALSE"
        assert f.message == "Use TRUE/FALSE, not T/F"
        assert f.file == ""
        assert f.line == 0
        assert f.cran_says == ""

    def test_finding_with_all_fields(self):
        f = check.Finding(
            rule_id="DESC-01",
            severity="warning",
            title="Title not in Title Case",
            message="Title Case issues found",
            file="DESCRIPTION",
            line=3,
            cran_says="Title must be in Title Case.",
        )
        assert f.file == "DESCRIPTION"
        assert f.line == 3
        assert f.cran_says == "Title must be in Title Case."


# ============================================================================
# Unit Tests: Title case checker
# ============================================================================


class TestTitleCase:
    """Tests for check_title_case()."""

    def test_correct_title_case(self):
        assert check.check_title_case("Bayesian Analysis of Sparse Data") == []

    def test_lowercase_first_word(self):
        problems = check.check_title_case("analysis of Data")
        assert any("analysis" in p for p in problems)

    def test_article_should_be_lowercase(self):
        problems = check.check_title_case("Analysis Of Data")
        assert any("Of" in p for p in problems)

    def test_preposition_should_be_lowercase(self):
        problems = check.check_title_case("Analysis In R")
        assert any("In" in p for p in problems)

    def test_acronyms_accepted(self):
        assert check.check_title_case("API Client for REST Services") == []

    def test_quoted_names_skipped(self):
        assert check.check_title_case("Interface to the 'dplyr' Package") == []

    def test_eg_allowed_lowercase(self):
        # e.g. should not trigger capitalization warning
        problems = check.check_title_case("Tools e.g. for Analysis")
        assert not any("e.g" in p for p in problems)


# ============================================================================
# Unit Tests: Software name detection
# ============================================================================


class TestSoftwareNames:
    """Tests for find_unquoted_software()."""

    def test_unquoted_python(self):
        result = check.find_unquoted_software("Interface to Python")
        assert "python" in result

    def test_quoted_python_ok(self):
        result = check.find_unquoted_software("Interface to 'Python'")
        assert "python" not in result

    def test_multiple_unquoted(self):
        result = check.find_unquoted_software("Uses TensorFlow and PyTorch")
        assert "tensorflow" in result
        assert "pytorch" in result

    def test_no_software(self):
        result = check.find_unquoted_software("Statistical analysis tools")
        assert result == []


# ============================================================================
# Unit Tests: DESCRIPTION parser
# ============================================================================


class TestParseDescription:
    """Tests for parse_description()."""

    def test_clean_package(self, clean_pkg):
        desc = check.parse_description(clean_pkg)
        assert desc["Package"] == "cleanpkg"
        assert desc["Version"] == "0.1.0"
        assert "Jane" in desc["Authors@R"]

    def test_problematic_package(self, problematic_pkg):
        desc = check.parse_description(problematic_pkg)
        assert desc["Package"] == "badpkg"
        assert desc.get("LazyData") == "true"
        assert "dplyr" in desc.get("Depends", "")

    def test_nonexistent_path(self, tmp_path):
        desc = check.parse_description(tmp_path / "nonexistent")
        assert desc == {}

    def test_multiline_field(self, clean_pkg):
        desc = check.parse_description(clean_pkg)
        # Description spans multiple lines
        assert "utility functions" in desc["Description"]


# ============================================================================
# Unit Tests: File scanning
# ============================================================================


class TestFileScanners:
    """Tests for file scanning functions."""

    def test_find_r_files(self, clean_pkg):
        files = check.find_r_files(clean_pkg)
        assert len(files) >= 1
        assert any(f.name == "hello.R" for f in files)

    def test_find_rd_files(self, clean_pkg):
        files = check.find_rd_files(clean_pkg)
        assert len(files) >= 1
        assert any(f.name == "hello.Rd" for f in files)

    def test_find_r_files_no_dir(self, tmp_path):
        assert check.find_r_files(tmp_path) == []

    def test_scan_file(self, clean_pkg):
        r_file = clean_pkg / "R" / "hello.R"
        matches = check.scan_file(r_file, r"function")
        assert len(matches) >= 1

    def test_scan_file_nonexistent(self, tmp_path):
        matches = check.scan_file(tmp_path / "nonexistent.R", r"pattern")
        assert matches == []

    def test_is_in_comment(self):
        assert check.is_in_comment("# This is a comment")
        assert check.is_in_comment("  # Indented comment")
        assert not check.is_in_comment("x <- 1  # trailing comment")
        assert not check.is_in_comment("x <- 1")


# ============================================================================
# Unit Tests: Closure detection
# ============================================================================


class TestClosureDetection:
    """Tests for _function_nesting_depth()."""

    def test_closure_depth(self, edge_cases_pkg):
        closures_file = edge_cases_pkg / "R" / "closures.R"
        # The <<- on line inside the increment function (nested inside make_counter)
        # should have depth >= 2
        text = closures_file.read_text()
        lines = text.splitlines()
        found_code_line = False
        for i, line in enumerate(lines, 1):
            if "<<-" in line and not line.strip().startswith("#"):
                found_code_line = True
                depth = check._function_nesting_depth(closures_file, i)
                assert depth >= 2, f"Expected depth >= 2 for <<- at line {i}, got {depth}"
        assert found_code_line, "Should have found at least one non-comment line with <<-"

    def test_top_level_function_depth(self, tmp_path):
        """A <<- at the top level of a function should have depth 1."""
        r_file = tmp_path / "test.R"
        r_file.write_text("my_func <- function() {\n  x <<- 1\n}\n")
        depth = check._function_nesting_depth(r_file, 2)
        assert depth == 1


# ============================================================================
# Unit Tests: Print method range detection
# ============================================================================


class TestPrintMethodRanges:
    """Tests for find_print_method_ranges() and find_display_helper_ranges()."""

    def test_print_method_ranges(self, edge_cases_pkg):
        f = edge_cases_pkg / "R" / "print_methods.R"
        ranges = check.find_print_method_ranges(f)
        assert len(ranges) >= 1, "Should find at least one print method range"

    def test_display_helper_ranges(self, edge_cases_pkg):
        f = edge_cases_pkg / "R" / "display_helpers.R"
        ranges = check.find_display_helper_ranges(f)
        assert len(ranges) >= 1, "Should find at least one display helper range"


# ============================================================================
# Unit Tests: NAMESPACE parser
# ============================================================================


class TestParseNamespace:
    """Tests for parse_namespace()."""

    def test_clean_namespace(self, clean_pkg):
        ns = check.parse_namespace(clean_pkg)
        assert ("hello", 1) in ns["exports"]

    def test_problematic_namespace(self, problematic_pkg):
        ns = check.parse_namespace(problematic_pkg)
        # Should have exportPattern
        assert len(ns["export_patterns"]) >= 1
        # Should have imports
        assert len(ns["imports"]) >= 2

    def test_edge_cases_namespace(self, edge_cases_pkg):
        ns = check.parse_namespace(edge_cases_pkg)
        assert len(ns["s3methods"]) >= 2  # print.myclass and format.myclass


# ============================================================================
# Unit Tests: Email helpers
# ============================================================================


class TestEmailHelpers:
    """Tests for email extraction and validation helpers."""

    def test_extract_cre_email(self):
        authors = 'person("Jane", "Doe", email = "jane@example.org", role = c("aut", "cre"))'
        assert check.extract_cre_email(authors) == "jane@example.org"

    def test_extract_cre_email_no_cre(self):
        authors = 'person("Jane", "Doe", email = "jane@example.org", role = c("aut"))'
        assert check.extract_cre_email(authors) is None

    def test_has_cre_without_email(self):
        authors = 'person("Jane", "Doe", role = c("aut", "cre"))'
        assert check._has_cre_without_email(authors)

    def test_has_cre_with_email(self):
        authors = 'person("Jane", "Doe", email = "jane@test.org", role = c("aut", "cre"))'
        assert not check._has_cre_without_email(authors)


# ============================================================================
# Unit Tests: Vignette helpers
# ============================================================================


class TestVignetteHelpers:
    """Tests for vignette-related helper functions."""

    def test_parse_vignette_metadata(self, tmp_path):
        vf = tmp_path / "test.Rmd"
        vf.write_text(
            "---\n"
            "title: My Vignette\n"
            "---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{My Vignette}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
        )
        meta = check.parse_vignette_metadata(vf)
        assert meta["engine"] is not None
        assert "knitr::rmarkdown" in meta["engine"][1]
        assert meta["index_entry"] is not None
        assert meta["encoding"] is not None
        assert meta["encoding"][1] == "UTF-8"

    def test_extract_packages_from_vignette(self, tmp_path):
        vf = tmp_path / "test.Rmd"
        vf.write_text(
            "---\ntitle: Test\n---\n"
            "```{r}\n"
            "library(dplyr)\n"
            "require(ggplot2)\n"
            "stats::median(1:10)\n"
            "```\n"
        )
        pkgs = check.extract_packages_from_vignette(vf)
        assert "dplyr" in pkgs
        assert "ggplot2" in pkgs
        assert "stats" in pkgs

    def test_parse_desc_packages(self):
        desc = {
            "Imports": "dplyr, ggplot2 (>= 3.0)",
            "Suggests": "testthat, knitr",
            "Depends": "R (>= 3.5.0)",
        }
        pkgs = check.parse_desc_packages(desc)
        assert "dplyr" in pkgs
        assert "ggplot2" in pkgs
        assert "testthat" in pkgs
        assert "knitr" in pkgs
        assert "R" not in pkgs  # R itself excluded


# ============================================================================
# Unit Tests: Data helpers
# ============================================================================


class TestDataHelpers:
    """Tests for data-related helper functions."""

    def test_is_valid_data_extension_rda(self, tmp_path):
        f = tmp_path / "data.rda"
        assert check._is_valid_data_extension(f)

    def test_is_valid_data_extension_csv(self, tmp_path):
        f = tmp_path / "data.csv"
        assert check._is_valid_data_extension(f)

    def test_is_valid_data_extension_compressed(self, tmp_path):
        f = tmp_path / "data.csv.gz"
        assert check._is_valid_data_extension(f)

    def test_is_valid_data_extension_rds_invalid(self, tmp_path):
        f = tmp_path / "data.rds"
        assert not check._is_valid_data_extension(f)

    def test_is_valid_data_extension_xlsx_invalid(self, tmp_path):
        f = tmp_path / "data.xlsx"
        assert not check._is_valid_data_extension(f)


# ============================================================================
# Integration Tests: Clean package
# ============================================================================


class TestCleanPackage:
    """Integration tests: clean package should produce minimal/no findings."""

    def test_description_checks(self, clean_pkg, clean_desc):
        findings = check.check_description_fields(clean_pkg, clean_desc)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0, f"Clean package should have no DESC errors: {[f.rule_id for f in errors]}"

    def test_code_checks(self, clean_pkg, clean_desc):
        findings = check.check_code(clean_pkg, clean_desc)
        assert len(findings) == 0, f"Clean package should have no code findings: {[f.rule_id for f in findings]}"

    def test_documentation_checks(self, clean_pkg, clean_desc):
        findings = check.check_documentation(clean_pkg, clean_desc)
        assert len(findings) == 0, f"Clean package should have no doc findings: {[f.rule_id for f in findings]}"

    def test_structure_checks(self, clean_pkg, clean_desc):
        findings = check.check_structure(clean_pkg, clean_desc)
        # May have notes (e.g., MISC-01 for NEWS.md format) but no errors
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0, f"Clean package should have no structure errors: {[f.rule_id for f in errors]}"

    def test_encoding_checks(self, clean_pkg, clean_desc):
        findings = check.check_encoding(clean_pkg, clean_desc)
        assert len(findings) == 0, f"Clean package should have no encoding findings: {[f.rule_id for f in findings]}"

    def test_namespace_checks(self, clean_pkg, clean_desc):
        findings = check.check_namespace(clean_pkg, clean_desc)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0, f"Clean package should have no NS errors: {[f.rule_id for f in errors]}"

    def test_email_checks(self, clean_pkg, clean_desc):
        findings = check.check_maintainer_email(clean_pkg, clean_desc)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0, f"Clean package should have no email errors: {[f.rule_id for f in errors]}"

    def test_full_check_via_cli(self, clean_pkg):
        """Run check.py via CLI and verify exit code 0."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(clean_pkg), "--severity", "error", "--fail-on", "error"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Clean package should pass: {result.stdout}\n{result.stderr}"


# ============================================================================
# Integration Tests: Problematic package
# ============================================================================


class TestProblematicPackage:
    """Integration tests: problematic package should trigger many findings."""

    def test_desc01_title_case(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-01" in rule_ids, "Should flag title case issues"

    def test_desc03_for_r_in_title(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-03" in rule_ids, "Should flag 'in R' in title"

    def test_desc04_description_opening(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-04" in rule_ids, "Should flag 'This package' in Description"

    def test_desc05_short_description(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-05" in rule_ids, "Should flag single-sentence Description"

    def test_desc08_missing_authors_r(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-08" in rule_ids, "Should flag missing Authors@R"

    def test_desc10_unnecessary_license_file(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-10" in rule_ids, "Should flag unnecessary + file LICENSE for GPL-3"

    def test_desc12_dev_version(self, problematic_pkg, problematic_desc):
        findings = check.check_description_fields(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-12" in rule_ids, "Should flag .9000 dev version"

    def test_code01_tf_usage(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-01" in rule_ids, "Should flag T/F usage"

    def test_code02_print_cat(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-02" in rule_ids, "Should flag print/cat usage"

    def test_code03_set_seed(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-03" in rule_ids, "Should flag set.seed()"

    def test_code04_options(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-04" in rule_ids, "Should flag options() without on.exit()"

    def test_code05_warn_minus_1(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-05" in rule_ids, "Should flag options(warn = -1)"

    def test_code06_getwd(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-06" in rule_ids, "Should flag getwd()"

    def test_code08_installed_packages(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-08" in rule_ids, "Should flag installed.packages()"

    def test_code09_global_assignment(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        code09_findings = [f for f in findings if f.rule_id == "CODE-09"]
        assert len(code09_findings) >= 1, "Should flag <<- and rm(list=ls())"

    def test_code11_quit(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-11" in rule_ids, "Should flag q()/quit()"

    def test_code12_triple_colon(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-12" in rule_ids, "Should flag ::: to base package"

    def test_code13_install_packages(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-13" in rule_ids, "Should flag install.packages()"

    def test_code15_browser(self, problematic_pkg, problematic_desc):
        findings = check.check_code(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-15" in rule_ids, "Should flag browser()"

    def test_doc01_missing_value(self, problematic_pkg, problematic_desc):
        findings = check.check_documentation(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-01" in rule_ids, "Should flag missing \\value in .Rd"

    def test_doc02_dontrun(self, problematic_pkg, problematic_desc):
        findings = check.check_documentation(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-02" in rule_ids, "Should flag \\dontrun{}"

    def test_ns01_import_conflicts(self, problematic_pkg, problematic_desc):
        findings = check.check_namespace(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-01" in rule_ids, "Should flag multiple full imports"

    def test_ns02_full_import(self, problematic_pkg, problematic_desc):
        findings = check.check_namespace(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-02" in rule_ids, "Should flag full namespace imports"

    def test_ns04_broad_export_pattern(self, problematic_pkg, problematic_desc):
        findings = check.check_namespace(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-04" in rule_ids, "Should flag broad exportPattern"

    def test_ns05_depends_misuse(self, problematic_pkg, problematic_desc):
        findings = check.check_namespace(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-05" in rule_ids, "Should flag dplyr in Depends"

    def test_data02_lazydata_no_data_dir(self, problematic_pkg, problematic_desc):
        findings = check.check_data(problematic_pkg, problematic_desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DATA-02" in rule_ids, "Should flag LazyData without data/"

    def test_full_check_via_cli_fails(self, problematic_pkg):
        """Run check.py via CLI and verify non-zero exit code."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(problematic_pkg), "--fail-on", "error"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0, "Problematic package should fail check"


# ============================================================================
# False-Positive Filtering Tests
# ============================================================================


class TestFalsePositiveFiltering:
    """Tests verifying that the checker does NOT flag valid patterns."""

    def test_closure_assignment_not_flagged(self, edge_cases_pkg, edge_cases_desc):
        """<<- inside closures should NOT be flagged as CODE-09."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        code09 = [f for f in findings if f.rule_id == "CODE-09"
                  and "closures.R" in f.file]
        assert len(code09) == 0, f"<<- in closures should not be flagged: {[f.message for f in code09]}"

    def test_print_in_print_method_not_flagged(self, edge_cases_pkg, edge_cases_desc):
        """print()/cat() inside print.* methods should NOT be flagged as CODE-02."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        code02_print_methods = [
            f for f in findings
            if f.rule_id == "CODE-02" and "print_methods.R" in f.file
        ]
        assert len(code02_print_methods) == 0, (
            f"print/cat in print methods should not be flagged: "
            f"{[(f.file, f.line, f.message) for f in code02_print_methods]}"
        )

    def test_cat_in_display_helpers_not_flagged(self, edge_cases_pkg, edge_cases_desc):
        """cat() inside display helper functions should NOT be flagged."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        code02_display = [
            f for f in findings
            if f.rule_id == "CODE-02" and "display_helpers.R" in f.file
        ]
        assert len(code02_display) == 0, (
            f"cat in display helpers should not be flagged: "
            f"{[(f.file, f.line, f.message) for f in code02_display]}"
        )

    def test_verbose_guard_not_flagged(self, edge_cases_pkg, edge_cases_desc):
        """cat/print guarded by verbose or interactive() should NOT be flagged."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        code02_verbose = [
            f for f in findings
            if f.rule_id == "CODE-02" and "verbose_guard.R" in f.file
        ]
        assert len(code02_verbose) == 0, (
            f"Verbose/interactive-guarded print should not be flagged: "
            f"{[(f.file, f.line, f.message) for f in code02_verbose]}"
        )

    def test_comments_not_flagged(self, edge_cases_pkg, edge_cases_desc):
        """Problematic patterns in comments should NOT be flagged."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        comments_findings = [
            f for f in findings if "comments.R" in f.file
        ]
        assert len(comments_findings) == 0, (
            f"Patterns in comments should not be flagged: "
            f"{[(f.rule_id, f.line, f.message) for f in comments_findings]}"
        )

    def test_reexport_rd_not_flagged_doc01(self, edge_cases_pkg, edge_cases_desc):
        """Reexport .Rd files with \\keyword{internal} should NOT trigger DOC-01."""
        findings = check.check_documentation(edge_cases_pkg, edge_cases_desc)
        doc01_reexport = [
            f for f in findings
            if f.rule_id == "DOC-01" and "reexports" in f.file
        ]
        assert len(doc01_reexport) == 0, (
            f"Reexport .Rd should not be flagged for missing \\value: "
            f"{[f.message for f in doc01_reexport]}"
        )

    def test_edge_case_package_no_code_errors(self, edge_cases_pkg, edge_cases_desc):
        """Edge cases package should have no code errors."""
        findings = check.check_code(edge_cases_pkg, edge_cases_desc)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0, (
            f"Edge cases should have no code errors: "
            f"{[(f.rule_id, f.file, f.line, f.message) for f in errors]}"
        )


# ============================================================================
# Unit Tests: Output formatting
# ============================================================================


class TestOutputFormatting:
    """Tests for output formatting functions."""

    def test_github_annotation_format(self):
        f = check.Finding(
            rule_id="CODE-01",
            severity="error",
            title="T/F instead of TRUE/FALSE",
            message="Use TRUE/FALSE",
            file="R/bad.R",
            line=10,
            cran_says="Please write TRUE and FALSE.",
        )
        result = check.format_github_annotation(f)
        assert result.startswith("::error ")
        assert "file=R/bad.R" in result
        assert "line=10" in result
        assert "[CODE-01]" in result
        assert "CRAN:" in result

    def test_github_annotation_no_file(self):
        f = check.Finding(
            rule_id="MISC-01",
            severity="note",
            title="No NEWS.md file",
            message="Create NEWS.md",
        )
        result = check.format_github_annotation(f)
        assert result.startswith("::notice ")
        assert "file=" not in result

    def test_github_annotation_warning(self):
        f = check.Finding(
            rule_id="CODE-02",
            severity="warning",
            title="Test Warning",
            message="A warning message",
            file="R/test.R",
        )
        result = check.format_github_annotation(f)
        assert result.startswith("::warning ")

    def test_console_format(self):
        f = check.Finding(
            rule_id="CODE-01",
            severity="error",
            title="T/F instead of TRUE/FALSE",
            message="Use TRUE/FALSE",
            file="R/bad.R",
            line=10,
        )
        result = check.format_console(f)
        assert "[CODE-01]" in result
        assert "R/bad.R:10" in result
        assert "Use TRUE/FALSE" in result

    def test_console_format_no_file(self):
        f = check.Finding(
            rule_id="MISC-01",
            severity="note",
            title="No NEWS.md file",
            message="Create NEWS.md",
        )
        result = check.format_console(f)
        assert "[MISC-01]" in result
        assert "(" not in result  # No file location parentheses


# ============================================================================
# CLI Integration Tests
# ============================================================================


class TestCLI:
    """Tests for command-line interface behavior."""

    def test_severity_filter_error_only(self, problematic_pkg):
        """--severity error should only show errors."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(problematic_pkg), "--severity", "error"],
            capture_output=True, text=True,
        )
        # Should show BLOCKING section but not WARNINGS or NOTES
        assert "BLOCKING" in result.stdout

    def test_severity_filter_note(self, clean_pkg):
        """--severity note on clean package should include notes too."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(clean_pkg), "--severity", "note", "--fail-on", "error"],
            capture_output=True, text=True,
        )
        # Should succeed
        assert result.returncode == 0

    def test_fail_on_warning(self, problematic_pkg):
        """--fail-on warning should fail when warnings exist."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(problematic_pkg), "--fail-on", "warning"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_fail_on_note(self, problematic_pkg):
        """--fail-on note should fail when notes exist."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(problematic_pkg), "--fail-on", "note"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_no_description_error(self, tmp_path):
        """Running on a non-package directory should fail with exit code 1."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(tmp_path)],
            capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "No DESCRIPTION" in result.stdout

    def test_output_contains_header(self, clean_pkg):
        """Output should contain the package name and version."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(clean_pkg), "--fail-on", "error"],
            capture_output=True, text=True,
        )
        assert "cleanpkg" in result.stdout
        assert "v0.1.0" in result.stdout

    def test_output_contains_summary(self, clean_pkg):
        """Output should contain a summary line with counts."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(clean_pkg), "--fail-on", "error"],
            capture_output=True, text=True,
        )
        assert "errors" in result.stdout
        assert "warnings" in result.stdout
        assert "notes" in result.stdout

    def test_github_annotations_in_ci(self, problematic_pkg):
        """When CI=true, should emit GitHub annotations."""
        import os
        env = os.environ.copy()
        env["CI"] = "true"
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(problematic_pkg), "--fail-on", "error"],
            capture_output=True, text=True, env=env,
        )
        # Should have at least one ::error annotation
        assert "::error" in result.stdout or "::warning" in result.stdout


# ============================================================================
# Unit Tests: Specific check functions on synthetic packages
# ============================================================================


class TestSyntheticChecks:
    """Tests using temporary synthetic packages for specific scenarios."""

    def _make_pkg(self, tmp_path, description_extra="", r_code="", rd_content="",
                  namespace_content="", has_news=True, has_cran_comments=True):
        """Helper to create a minimal synthetic package."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "R").mkdir()
        (pkg / "man").mkdir()

        desc_text = (
            "Package: testpkg\n"
            "Type: Package\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        if description_extra:
            desc_text += description_extra + "\n"
        (pkg / "DESCRIPTION").write_text(desc_text)
        (pkg / "LICENSE").write_text("YEAR: 2024\nCOPYRIGHT HOLDER: Test User\n")

        if namespace_content:
            (pkg / "NAMESPACE").write_text(namespace_content)
        else:
            (pkg / "NAMESPACE").write_text("export(test_fn)\n")

        if r_code:
            (pkg / "R" / "code.R").write_text(r_code)

        if rd_content:
            (pkg / "man" / "test.Rd").write_text(rd_content)

        if has_news:
            (pkg / "NEWS.md").write_text("# testpkg 0.1.0\n\n* Initial release.\n")
        if has_cran_comments:
            (pkg / "cran-comments.md").write_text("## R CMD check results\n\n0 errors | 0 warnings | 0 notes\n")

        return pkg

    def test_desc06_doi_space(self, tmp_path):
        """DESC-06: Space after doi: should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra='Description: Implements methods from Doe (2023) <doi: 10.1234/test>.\n    Second sentence here.',
        )
        # Overwrite DESCRIPTION to include doi in Description
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Implements methods from Doe (2023) <doi: 10.1234/test>.\n"
            "    Second sentence here for completeness.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-06" in rule_ids

    def test_desc09_missing_cph(self, tmp_path):
        """DESC-09: Missing cph role should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-09" in rule_ids

    def test_desc11_no_cre(self, tmp_path):
        """DESC-11: No cre role should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cph"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-11" in rule_ids

    def test_desc15_smart_quotes(self, tmp_path):
        """DESC-15: Smart/curly quotes should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides \u2018smart\u2019 functionality for testing.\n"
            "    This is a second sentence.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DESC-15" in rule_ids

    def test_email01_mailing_list(self, tmp_path):
        """EMAIL-01: Mailing list email should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "dev@googlegroups.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality.\n    Second sentence here.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_maintainer_email(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "EMAIL-01" in rule_ids

    def test_email03_disposable(self, tmp_path):
        """EMAIL-03: Disposable email should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "john.smith@mailinator.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality.\n    Second sentence here.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_maintainer_email(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "EMAIL-03" in rule_ids

    def test_email04_placeholder(self, tmp_path):
        """EMAIL-04: Placeholder email should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "user@example.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality.\n    Second sentence here.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_maintainer_email(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "EMAIL-04" in rule_ids

    def test_email06_noreply(self, tmp_path):
        """EMAIL-06: Noreply email should be flagged."""
        pkg = self._make_pkg(tmp_path)
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "noreply@company.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality.\n    Second sentence here.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_maintainer_email(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "EMAIL-06" in rule_ids

    def test_enc03_non_portable_escape(self, tmp_path):
        """ENC-03: Non-portable \\x escape should be flagged."""
        pkg = self._make_pkg(tmp_path, r_code='x <- "\\x80\\x81"\n')
        desc = check.parse_description(pkg)
        findings = check.check_encoding(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "ENC-03" in rule_ids

    def test_structure_binary_file(self, tmp_path):
        """PLAT-02: Binary files should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.o").write_bytes(b"\x00\x01\x02\x03")
        desc = check.parse_description(pkg)
        findings = check.check_structure(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "PLAT-02" in rule_ids

    def test_misc01_no_news(self, tmp_path):
        """MISC-01: Missing NEWS.md should be noted."""
        pkg = self._make_pkg(tmp_path, has_news=False)
        desc = check.parse_description(pkg)
        findings = check.check_structure(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "MISC-01" in rule_ids

    def test_doc01_roxygen_missing_return(self, tmp_path):
        """DOC-01: Exported function without @return should be flagged."""
        r_code = (
            "#' My Function\n"
            "#'\n"
            "#' @param x A value.\n"
            "#' @export\n"
            "my_func <- function(x) {\n"
            "    x + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-01" in rule_ids

    def test_doc01_roxygen_with_return_ok(self, tmp_path):
        """DOC-01: Exported function WITH @return should NOT be flagged."""
        r_code = (
            "#' My Function\n"
            "#'\n"
            "#' @param x A value.\n"
            "#' @return The incremented value.\n"
            "#' @export\n"
            "my_func <- function(x) {\n"
            "    x + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc01 = [f for f in findings if f.rule_id == "DOC-01"]
        assert len(doc01) == 0

    def test_doc01_rdname_not_flagged(self, tmp_path):
        """DOC-01: Functions with @rdname should NOT be flagged."""
        r_code = (
            "#' My Function\n"
            "#'\n"
            "#' @rdname my_funcs\n"
            "#' @export\n"
            "my_func <- function(x) {\n"
            "    x + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc01 = [f for f in findings if f.rule_id == "DOC-01"]
        assert len(doc01) == 0

    def test_doc01_keywords_internal_not_flagged(self, tmp_path):
        """DOC-01: Functions with @keywords internal should NOT be flagged."""
        r_code = (
            "#' Internal Helper\n"
            "#'\n"
            "#' @keywords internal\n"
            "#' @export\n"
            "internal_func <- function(x) {\n"
            "    x + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc01 = [f for f in findings if f.rule_id == "DOC-01"]
        assert len(doc01) == 0

    def test_doc05_missing_examples(self, tmp_path):
        """DOC-05: Exported function without @examples should get a note."""
        r_code = (
            "#' My Function\n"
            "#'\n"
            "#' @param x A value.\n"
            "#' @return The incremented value.\n"
            "#' @export\n"
            "my_func <- function(x) {\n"
            "    x + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-05" in rule_ids

    def test_inst01_hidden_files(self, tmp_path):
        """INST-01: Hidden files in inst/ should be flagged."""
        pkg = self._make_pkg(tmp_path)
        inst = pkg / "inst"
        inst.mkdir()
        (inst / ".DS_Store").write_bytes(b"\x00")
        desc = check.parse_description(pkg)
        findings = check.check_inst_directory(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "INST-01" in rule_ids

    def test_inst04_reserved_dir(self, tmp_path):
        """INST-04: Reserved directory name in inst/ should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "inst" / "R").mkdir(parents=True)
        (pkg / "inst" / "R" / "dummy.R").write_text("# dummy\n")
        desc = check.parse_description(pkg)
        findings = check.check_inst_directory(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "INST-04" in rule_ids

    def test_data01_undocumented_dataset(self, tmp_path):
        """DATA-01: Undocumented dataset should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "data").mkdir()
        (pkg / "data" / "mydata.rda").write_bytes(b"\x00\x01\x02")
        desc = check.parse_description(pkg)
        findings = check.check_data(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DATA-01" in rule_ids

    def test_comp05_bash_shebang(self, tmp_path):
        """COMP-05: configure with #!/bin/bash should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "configure").write_text("#!/bin/bash\necho 'hello'\n")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-05" in rule_ids

    # --- CODE-07: Clean up temporary files ---

    def test_code07_tempfile_no_cleanup(self, tmp_path):
        """CODE-07: tempfile() without unlink/on.exit should be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    tmp <- tempfile()\n"
            "    writeLines(x, tmp)\n"
            "    readLines(tmp)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-07" in rule_ids

    def test_code07_tempfile_with_unlink_ok(self, tmp_path):
        """CODE-07: tempfile() with unlink() should NOT be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    tmp <- tempfile()\n"
            "    writeLines(x, tmp)\n"
            "    result <- readLines(tmp)\n"
            "    unlink(tmp)\n"
            "    result\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code07 = [f for f in findings if f.rule_id == "CODE-07"]
        assert len(code07) == 0

    def test_code07_tempfile_with_on_exit_ok(self, tmp_path):
        """CODE-07: tempfile() with on.exit() should NOT be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    tmp <- tempfile()\n"
            "    on.exit(unlink(tmp), add = TRUE)\n"
            "    writeLines(x, tmp)\n"
            "    readLines(tmp)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code07 = [f for f in findings if f.rule_id == "CODE-07"]
        assert len(code07) == 0

    def test_code07_tempdir_no_cleanup(self, tmp_path):
        """CODE-07: tempdir() without cleanup should be flagged."""
        r_code = (
            "save_output <- function(x) {\n"
            "    dir <- tempdir()\n"
            "    writeLines(x, file.path(dir, 'out.txt'))\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-07" in rule_ids

    # --- CODE-10: Maximum 2 cores ---

    def test_code10_detectCores_uncapped(self, tmp_path):
        """CODE-10: detectCores() without min(..., 2) should be flagged."""
        r_code = (
            "run_parallel <- function(x) {\n"
            "    ncores <- parallel::detectCores()\n"
            "    parallel::mclapply(x, identity, mc.cores = ncores)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-10" in rule_ids

    def test_code10_detectCores_capped_ok(self, tmp_path):
        """CODE-10: detectCores() with min(..., 2) should NOT be flagged."""
        r_code = (
            "run_parallel <- function(x) {\n"
            "    ncores <- min(parallel::detectCores(), 2)\n"
            "    parallel::mclapply(x, identity, mc.cores = ncores)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code10 = [f for f in findings if f.rule_id == "CODE-10"]
        assert len(code10) == 0

    def test_code10_mc_cores_option_ok(self, tmp_path):
        """CODE-10: getOption('mc.cores') should NOT be flagged."""
        r_code = (
            "run_parallel <- function(x) {\n"
            "    ncores <- getOption('mc.cores', 2L)\n"
            "    parallel::mclapply(x, identity, mc.cores = ncores)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code10 = [f for f in findings if f.rule_id == "CODE-10"]
        assert len(code10) == 0

    def test_code10_omp_num_threads(self, tmp_path):
        """CODE-10: Setting OMP_NUM_THREADS should be flagged."""
        r_code = (
            "setup <- function() {\n"
            '    Sys.setenv("OMP_NUM_THREADS" = 4)\n'
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-10" in rule_ids

    # --- CODE-14: No disabling SSL/TLS verification ---

    def test_code14_ssl_verifypeer_false(self, tmp_path):
        """CODE-14: ssl_verifypeer = FALSE should be flagged."""
        r_code = (
            "fetch_data <- function(url) {\n"
            "    httr::GET(url, httr::config(ssl_verifypeer = FALSE))\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-14" in rule_ids

    def test_code14_ssl_verifypeer_zero(self, tmp_path):
        """CODE-14: ssl_verifypeer = 0 should be flagged."""
        r_code = (
            "fetch_data <- function(url) {\n"
            "    httr::GET(url, httr::config(ssl_verifypeer = 0))\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-14" in rule_ids

    def test_code14_ssl_verifypeer_true_ok(self, tmp_path):
        """CODE-14: ssl_verifypeer = TRUE should NOT be flagged."""
        r_code = (
            "fetch_data <- function(url) {\n"
            "    httr::GET(url, httr::config(ssl_verifypeer = TRUE))\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code14 = [f for f in findings if f.rule_id == "CODE-14"]
        assert len(code14) == 0

    # --- CODE-17: UseLTO causes CPU time NOTE ---

    def test_code17_uselto(self, tmp_path):
        """CODE-17: UseLTO in DESCRIPTION should be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="UseLTO: yes")
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-17" in rule_ids

    def test_code17_no_uselto_ok(self, tmp_path):
        """CODE-17: No UseLTO should NOT produce CODE-17 finding."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_description_fields(pkg, desc)
        code17 = [f for f in findings if f.rule_id == "CODE-17"]
        assert len(code17) == 0

    # --- CODE-21: class(matrix()) returns two-element vector ---

    def test_code21_class_eq_matrix(self, tmp_path):
        """CODE-21: class(x) == 'matrix' should be flagged."""
        r_code = (
            "check_type <- function(x) {\n"
            '    if (class(x) == "matrix") return(TRUE)\n'
            "    FALSE\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-21" in rule_ids

    def test_code21_class_eq_data_frame(self, tmp_path):
        """CODE-21: class(x) == 'data.frame' should be flagged."""
        r_code = (
            "check_type <- function(x) {\n"
            '    if (class(x) == "data.frame") return(TRUE)\n'
            "    FALSE\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-21" in rule_ids

    def test_code21_inherits_ok(self, tmp_path):
        """CODE-21: inherits(x, 'matrix') should NOT be flagged."""
        r_code = (
            "check_type <- function(x) {\n"
            '    if (inherits(x, "matrix")) return(TRUE)\n'
            "    FALSE\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code21 = [f for f in findings if f.rule_id == "CODE-21"]
        assert len(code21) == 0

    # --- CODE-22: if()/while() condition length > 1 ---

    def test_code22_if_class(self, tmp_path):
        """CODE-22: if(class(x) == ...) should be flagged."""
        r_code = (
            "check_type <- function(x) {\n"
            '    if (class(x) == "numeric") {\n'
            "        return(TRUE)\n"
            "    }\n"
            "    FALSE\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-22" in rule_ids

    def test_code22_if_inherits_ok(self, tmp_path):
        """CODE-22: if(inherits(x, ...)) should NOT be flagged."""
        r_code = (
            "check_type <- function(x) {\n"
            '    if (inherits(x, "numeric")) {\n'
            "        return(TRUE)\n"
            "    }\n"
            "    FALSE\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code22 = [f for f in findings if f.rule_id == "CODE-22"]
        assert len(code22) == 0

    # --- CODE-19: Staged installation compatibility ---

    def test_code19_top_level_system_file(self, tmp_path):
        """CODE-19: Top-level system.file() assignment should be flagged."""
        r_code = (
            "DB_PATH <- system.file('extdata', 'db.sqlite', package = 'testpkg')\n"
            "\n"
            "get_data <- function() {\n"
            "    readLines(DB_PATH)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-19" in rule_ids

    def test_code19_system_file_in_function_ok(self, tmp_path):
        """CODE-19: system.file() inside a function should NOT be flagged."""
        r_code = (
            "get_db_path <- function() {\n"
            "    system.file('extdata', 'db.sqlite', package = 'testpkg')\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code19 = [f for f in findings if f.rule_id == "CODE-19"]
        assert len(code19) == 0

    # --- NS-08: No library()/require() in package code ---

    def test_ns08_library_in_code(self, tmp_path):
        """NS-08: library() in package code should be flagged."""
        r_code = (
            "do_stuff <- function() {\n"
            "    library(dplyr)\n"
            "    mtcars %>% filter(mpg > 20)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-08" in rule_ids

    def test_ns08_require_in_code(self, tmp_path):
        """NS-08: require() in package code should be flagged."""
        r_code = (
            "do_stuff <- function() {\n"
            "    require(ggplot2)\n"
            "    ggplot(mtcars, aes(x = mpg))\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-08" in rule_ids

    def test_ns08_requireNamespace_ok(self, tmp_path):
        """NS-08: requireNamespace() should NOT be flagged."""
        r_code = (
            "do_stuff <- function() {\n"
            '    if (requireNamespace("dplyr", quietly = TRUE)) {\n'
            "        dplyr::filter(mtcars, mpg > 20)\n"
            "    }\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        ns08 = [f for f in findings if f.rule_id == "NS-08"]
        assert len(ns08) == 0

    def test_ns08_library_in_comment_ok(self, tmp_path):
        """NS-08: library() in a comment should NOT be flagged."""
        r_code = (
            "# library(dplyr) -- not actually loaded\n"
            "do_stuff <- function() {\n"
            "    dplyr::filter(mtcars, mpg > 20)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        ns08 = [f for f in findings if f.rule_id == "NS-08"]
        assert len(ns08) == 0

    def test_ns08_library_in_interactive_ok(self, tmp_path):
        """NS-08: library() inside if(interactive()) should NOT be flagged."""
        r_code = (
            "setup <- function() {\n"
            "    if (interactive()) library(devtools)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        ns08 = [f for f in findings if f.rule_id == "NS-08"]
        assert len(ns08) == 0

    # --- COMP-01: C23 keyword conflicts ---

    def test_comp01_define_bool(self, tmp_path):
        """COMP-01: #define bool should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "#define bool int\n"
            "void my_func(void) { }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-01" in rule_ids

    def test_comp01_define_true(self, tmp_path):
        """COMP-01: #define true should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "#define true 1\n"
            "#define false 0\n"
            "void my_func(void) { }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-01" in rule_ids

    def test_comp01_typedef_bool(self, tmp_path):
        """COMP-01: typedef ... bool should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "types.h").write_text(
            "#ifndef TYPES_H\n"
            "#define TYPES_H\n"
            "typedef int bool;\n"
            "#endif\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-01" in rule_ids

    def test_comp01_stdbool_include_ok(self, tmp_path):
        """COMP-01: Using stdbool.h should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "#include <stdbool.h>\n"
            "bool my_flag = true;\n"
            "void my_func(void) { }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp01 = [f for f in findings if f.rule_id == "COMP-01"]
        assert len(comp01) == 0

    # --- COMP-03: Non-API entry points ---

    def test_comp03_dataptr(self, tmp_path):
        """COMP-03: DATAPTR should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "#include <Rinternals.h>\n"
            "SEXP get_data(SEXP x) {\n"
            "    double *ptr = DATAPTR(x);\n"
            "    return R_NilValue;\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-03" in rule_ids

    def test_comp03_set_typeof(self, tmp_path):
        """COMP-03: SET_TYPEOF should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "#include <Rinternals.h>\n"
            "void change_type(SEXP x) {\n"
            "    SET_TYPEOF(x, INTSXP);\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-03" in rule_ids

    # --- COMP-09: Rust package requirements ---

    def test_comp09_cargo_no_vendor(self, tmp_path):
        """COMP-09: Cargo.toml without vendor/ should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Cargo.toml").write_text("[package]\nname = 'test'\n")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-09" in rule_ids

    def test_comp09_cargo_no_configure(self, tmp_path):
        """COMP-09: Cargo.toml without configure script should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Cargo.toml").write_text("[package]\nname = 'test'\n")
        (pkg / "src" / "vendor").mkdir()
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp09 = [f for f in findings if f.rule_id == "COMP-09"]
        # Should flag missing configure
        assert any("configure" in f.message for f in comp09)

    def test_comp09_cargo_complete_ok(self, tmp_path):
        """COMP-09: Cargo.toml with vendor/ and configure should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Cargo.toml").write_text("[package]\nname = 'test'\n")
        (pkg / "src" / "vendor").mkdir()
        (pkg / "configure").write_text("#!/bin/sh\nrustc --version\n")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp09 = [f for f in findings if f.rule_id == "COMP-09"]
        assert len(comp09) == 0

    # --- COMP-10: Native routine registration ---

    def test_comp10_missing_registration(self, tmp_path):
        """COMP-10: .Call() without init.c should be flagged."""
        r_code = (
            "compute <- function(x) {\n"
            '    .Call("C_compute", x)\n'
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, namespace_content="export(compute)\n")
        (pkg / "src").mkdir()
        (pkg / "src" / "compute.c").write_text(
            "#include <R.h>\n"
            "#include <Rinternals.h>\n"
            "SEXP C_compute(SEXP x) { return x; }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-10" in rule_ids

    def test_comp10_with_registration_ok(self, tmp_path):
        """COMP-10: .Call() with proper init.c should NOT be flagged for missing registration."""
        r_code = (
            "compute <- function(x) {\n"
            '    .Call("C_compute", x)\n'
            "}\n"
        )
        pkg = self._make_pkg(
            tmp_path, r_code=r_code,
            namespace_content="export(compute)\nuseDynLib(testpkg, .registration = TRUE)\n"
        )
        (pkg / "src").mkdir()
        (pkg / "src" / "compute.c").write_text(
            "#include <R.h>\n"
            "#include <Rinternals.h>\n"
            "SEXP C_compute(SEXP x) { return x; }\n"
        )
        (pkg / "src" / "init.c").write_text(
            "#include <R.h>\n"
            "#include <R_ext/Rdynload.h>\n"
            "void R_init_testpkg(DllInfo *dll) {\n"
            "    R_registerRoutines(dll, NULL, NULL, NULL, NULL);\n"
            "    R_useDynamicSymbols(dll, FALSE);\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp10 = [f for f in findings if f.rule_id == "COMP-10"]
        assert len(comp10) == 0

    # --- COMP-12: UCRT Windows toolchain ---

    def test_comp12_mingw_prefix(self, tmp_path):
        """COMP-12: $(MINGW_PREFIX) in Makevars.win should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Makevars.win").write_text(
            "PKG_LIBS = -L$(MINGW_PREFIX)/lib -lfoo\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-12" in rule_ids

    def test_comp12_download_file(self, tmp_path):
        """COMP-12: download.file in configure.win should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "configure.win").write_text(
            "#!/bin/sh\n"
            "download.file('https://example.com/lib.dll', 'src/lib.dll')\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "COMP-12" in rule_ids

    def test_comp12_clean_makevars_win_ok(self, tmp_path):
        """COMP-12: Clean Makevars.win should NOT produce COMP-12 findings."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Makevars.win").write_text(
            "PKG_LIBS = -lfoo\n"
            "PKG_CFLAGS = -Wall\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp12 = [f for f in findings if f.rule_id == "COMP-12"]
        assert len(comp12) == 0

    # --- DOC-07: Use Canonical CRAN/Bioconductor URLs ---

    def test_doc07_non_canonical_cran_url(self, tmp_path):
        """DOC-07: Non-canonical CRAN URL should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{See http://cran.r-project.org/web/packages/foo/index.html}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-07" in rule_ids

    def test_doc07_canonical_cran_url_ok(self, tmp_path):
        """DOC-07: Canonical CRAN URL should NOT be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{See https://CRAN.R-project.org/package=foo}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc07 = [f for f in findings if f.rule_id == "DOC-07"]
        assert len(doc07) == 0

    def test_doc07_non_canonical_bioc_url(self, tmp_path):
        """DOC-07: Non-canonical Bioconductor URL should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{See http://www.bioconductor.org/packages/foo}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-07" in rule_ids

    # --- DOC-08: Lost Braces in Rd Documentation ---

    def test_doc08_itemize_with_brace_items(self, tmp_path):
        """DOC-08: \\item{}{} inside \\itemize should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\details{\n"
            "\\itemize{\n"
            "  \\item{first}{This is the first item}\n"
            "  \\item{second}{This is the second item}\n"
            "}\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-08" in rule_ids

    def test_doc08_describe_with_brace_items_ok(self, tmp_path):
        """DOC-08: \\item{}{} inside \\describe is correct and should NOT be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\details{\n"
            "\\describe{\n"
            "  \\item{first}{This is the first item}\n"
            "  \\item{second}{This is the second item}\n"
            "}\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc08 = [f for f in findings if f.rule_id == "DOC-08"]
        assert len(doc08) == 0

    # --- DOC-09: HTML5 Rd Validation ---

    def test_doc09_deprecated_html_font(self, tmp_path):
        """DOC-09: <font> tag in \\out{} block should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            '\\if{html}{\\out{<font color="red">Warning</font>}}\n'
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-09" in rule_ids

    def test_doc09_html5_ok(self, tmp_path):
        """DOC-09: Modern HTML5 elements should NOT be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            '\\if{html}{\\out{<span style="color:red">Warning</span>}}\n'
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc09 = [f for f in findings if f.rule_id == "DOC-09"]
        assert len(doc09) == 0

    # --- DOC-10: \\donttest Examples Now Executed Under --as-cran ---

    def test_doc10_donttest_in_rd(self, tmp_path):
        """DOC-10: \\donttest{} in Rd should produce a NOTE."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\examples{\n"
            "\\donttest{\n"
            "  slow_computation()\n"
            "}\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-10" in rule_ids

    def test_doc10_no_donttest_ok(self, tmp_path):
        """DOC-10: No \\donttest{} should NOT produce DOC-10."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\examples{\n"
            "  test()\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc10 = [f for f in findings if f.rule_id == "DOC-10"]
        assert len(doc10) == 0

    # --- DOC-11: Duplicated Vignette Titles ---

    def test_doc11_duplicate_vignette_titles(self, tmp_path):
        """DOC-11: Duplicate vignette titles should be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown")
        (pkg / "vignettes").mkdir()
        for name in ("vig1.Rmd", "vig2.Rmd"):
            (pkg / "vignettes" / name).write_text(
                "---\ntitle: My Vignette\n---\n"
                "<!--\n"
                "%\\VignetteEngine{knitr::rmarkdown}\n"
                "%\\VignetteIndexEntry{My Vignette}\n"
                "%\\VignetteEncoding{UTF-8}\n"
                "-->\n"
                "Hello world.\n"
            )
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-11" in rule_ids

    def test_doc11_unique_vignette_titles_ok(self, tmp_path):
        """DOC-11: Unique vignette titles should NOT be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown")
        (pkg / "vignettes").mkdir()
        for i, name in enumerate(("vig1.Rmd", "vig2.Rmd")):
            (pkg / "vignettes" / name).write_text(
                f"---\ntitle: Vignette {i}\n---\n"
                "<!--\n"
                "%\\VignetteEngine{knitr::rmarkdown}\n"
                f"%\\VignetteIndexEntry{{Vignette {i}}}\n"
                "%\\VignetteEncoding{UTF-8}\n"
                "-->\n"
                "Hello world.\n"
            )
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc11 = [f for f in findings if f.rule_id == "DOC-11"]
        assert len(doc11) == 0

    # --- NS-07: Re-Export Documentation ---

    def test_ns07_undocumented_reexport(self, tmp_path):
        """NS-07: Re-exported function without documentation should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            namespace_content="importFrom(magrittr, \"%>%\")\nexport(\"%>%\")\nexport(test_fn)\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_namespace(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NS-07" in rule_ids

    def test_ns07_documented_reexport_ok(self, tmp_path):
        """NS-07: Re-exported function WITH documentation should NOT be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            namespace_content="importFrom(magrittr, \"%>%\")\nexport(\"%>%\")\nexport(test_fn)\n"
        )
        # Create documentation for the re-export
        rd_content = (
            "\\name{\\%>\\%}\n"
            "\\alias{\\%>\\%}\n"
            "\\title{Pipe operator}\n"
            "\\description{See magrittr}\n"
            "\\value{Result of piped expression.}\n"
        )
        (pkg / "man" / "reexports.Rd").write_text(rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_namespace(pkg, desc)
        ns07 = [f for f in findings if f.rule_id == "NS-07"]
        assert len(ns07) == 0

    # --- DEP-02: Suggested Packages Must Be Used Conditionally ---

    def test_dep02_unconditional_library(self, tmp_path):
        """DEP-02: library(suggested_pkg) without conditional should be flagged."""
        r_code = (
            "do_analysis <- function(x) {\n"
            "    library(ggplot2)\n"
            "    ggplot(x, aes(x = val)) + geom_histogram()\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="Suggests: ggplot2")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DEP-02" in rule_ids

    def test_dep02_conditional_require_ok(self, tmp_path):
        """DEP-02: require() inside if() should NOT be flagged as DEP-02."""
        r_code = (
            "do_analysis <- function(x) {\n"
            "    if (require(ggplot2)) {\n"
            "        ggplot(x, aes(x = val)) + geom_histogram()\n"
            "    }\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="Suggests: ggplot2")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        dep02 = [f for f in findings if f.rule_id == "DEP-02"]
        assert len(dep02) == 0

    def test_dep02_requireNamespace_ok(self, tmp_path):
        """DEP-02: requireNamespace() should NOT be flagged as DEP-02."""
        r_code = (
            "do_analysis <- function(x) {\n"
            "    if (requireNamespace(\"ggplot2\", quietly = TRUE)) {\n"
            "        ggplot2::ggplot(x, ggplot2::aes(x = val)) + ggplot2::geom_histogram()\n"
            "    }\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code, description_extra="Suggests: ggplot2")
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        dep02 = [f for f in findings if f.rule_id == "DEP-02"]
        assert len(dep02) == 0

    def test_dep02_imports_pkg_not_flagged(self, tmp_path):
        """DEP-02: library() for a non-Suggests package should NOT be flagged as DEP-02."""
        r_code = (
            "do_stuff <- function() {\n"
            "    library(dplyr)\n"
            "    mtcars %>% filter(mpg > 20)\n"
            "}\n"
        )
        # dplyr is NOT in Suggests, so DEP-02 should not fire (NS-08 might though)
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        dep02 = [f for f in findings if f.rule_id == "DEP-02"]
        assert len(dep02) == 0

    # --- NET-01: Must Fail Gracefully When Resources Unavailable ---

    def test_net01_bare_download_file(self, tmp_path):
        """NET-01: download.file() without error handling should be flagged."""
        r_code = (
            "get_data <- function(url) {\n"
            "    tmp <- tempfile()\n"
            "    download.file(url, tmp)\n"
            "    readLines(tmp)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "NET-01" in rule_ids

    def test_net01_with_trycatch_ok(self, tmp_path):
        """NET-01: download.file() with tryCatch should NOT be flagged."""
        r_code = (
            "get_data <- function(url) {\n"
            "    tmp <- tempfile()\n"
            "    tryCatch(\n"
            "        download.file(url, tmp),\n"
            "        error = function(e) NULL\n"
            "    )\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        net01 = [f for f in findings if f.rule_id == "NET-01"]
        assert len(net01) == 0

    def test_net01_with_try_ok(self, tmp_path):
        """NET-01: httr::GET() with try() should NOT be flagged."""
        r_code = (
            "get_data <- function(url) {\n"
            "    result <- try(httr::GET(url), silent = TRUE)\n"
            "    if (inherits(result, 'try-error')) return(NULL)\n"
            "    result\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        net01 = [f for f in findings if f.rule_id == "NET-01"]
        assert len(net01) == 0

    # --- DATA-07: Serialization Version Incompatibility ---

    def test_data07_v3_no_r_constraint(self, tmp_path):
        """DATA-07: RDX3 data without R version constraint should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "data").mkdir()
        # Write a file that starts with RDX3 magic
        (pkg / "data" / "mydata.rda").write_bytes(b"RDX3\x00\x00\x00" + b"\x00" * 50)
        desc = check.parse_description(pkg)
        findings = check.check_data(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DATA-07" in rule_ids

    def test_data07_v3_with_r35_ok(self, tmp_path):
        """DATA-07: RDX3 data with R >= 3.5.0 should NOT be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="Depends: R (>= 3.5.0)")
        (pkg / "data").mkdir()
        (pkg / "data" / "mydata.rda").write_bytes(b"RDX3\x00\x00\x00" + b"\x00" * 50)
        desc = check.parse_description(pkg)
        findings = check.check_data(pkg, desc)
        data07 = [f for f in findings if f.rule_id == "DATA-07"]
        assert len(data07) == 0

    def test_data07_v3_with_old_r_version(self, tmp_path):
        """DATA-07: RDX3 data with R >= 3.4.0 should be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="Depends: R (>= 3.4.0)")
        (pkg / "data").mkdir()
        (pkg / "data" / "mydata.rda").write_bytes(b"RDX3\x00\x00\x00" + b"\x00" * 50)
        desc = check.parse_description(pkg)
        findings = check.check_data(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DATA-07" in rule_ids

    def test_data07_v2_ok(self, tmp_path):
        """DATA-07: Non-v3 data should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "data").mkdir()
        # Write a file with RDX2 magic (serialization v2)
        (pkg / "data" / "mydata.rda").write_bytes(b"RDX2\x00\x00\x00" + b"\x00" * 50)
        desc = check.parse_description(pkg)
        findings = check.check_data(pkg, desc)
        data07 = [f for f in findings if f.rule_id == "DATA-07"]
        assert len(data07) == 0

    # --- SYS-03: C++20 Default Standard Transition ---

    def test_sys03_cxx17_explicit(self, tmp_path):
        """SYS-03: CXX_STD = CXX17 should produce an informational NOTE."""
        pkg = self._make_pkg(tmp_path, description_extra="SystemRequirements: C++17")
        (pkg / "src").mkdir()
        (pkg / "src" / "Makevars").write_text("CXX_STD = CXX17\n")
        (pkg / "src" / "code.cpp").write_text("// C++ code\n")
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "SYS-03" in rule_ids

    def test_sys03_cxx11_deprecated(self, tmp_path):
        """SYS-03: CXX_STD = CXX11 should be flagged as deprecated."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Makevars").write_text("CXX_STD = CXX11\n")
        (pkg / "src" / "code.cpp").write_text("// C++ code\n")
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        sys03 = [f for f in findings if f.rule_id == "SYS-03"]
        assert len(sys03) >= 1
        assert any("deprecated" in f.message.lower() or "C++11" in f.message for f in sys03)

    def test_sys03_no_cxx_std_ok(self, tmp_path):
        """SYS-03: No CXX_STD should NOT produce SYS-03 finding."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "Makevars").write_text("PKG_CFLAGS = -Wall\n")
        (pkg / "src" / "code.cpp").write_text("// C++ code\n")
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        sys03 = [f for f in findings if f.rule_id == "SYS-03"]
        assert len(sys03) == 0

    # --- SYS-04: Configure Script Missing for System Libraries ---

    def test_sys04_missing_configure(self, tmp_path):
        """SYS-04: Compiled code with SystemRequirements but no configure should be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="SystemRequirements: libcurl")
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "void my_func(void) { }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "SYS-04" in rule_ids

    def test_sys04_with_configure_ok(self, tmp_path):
        """SYS-04: Compiled code with configure should NOT be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="SystemRequirements: libcurl")
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "void my_func(void) { }\n"
        )
        (pkg / "configure").write_text("#!/bin/sh\necho 'checking libcurl...'\n")
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        sys04 = [f for f in findings if f.rule_id == "SYS-04"]
        assert len(sys04) == 0

    def test_sys04_with_configure_ac_ok(self, tmp_path):
        """SYS-04: configure.ac should count as having a configure script."""
        pkg = self._make_pkg(tmp_path, description_extra="SystemRequirements: libcurl")
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "void my_func(void) { }\n"
        )
        (pkg / "configure.ac").write_text("AC_INIT\n")
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        sys04 = [f for f in findings if f.rule_id == "SYS-04"]
        assert len(sys04) == 0

    def test_sys04_no_sysreqs_ok(self, tmp_path):
        """SYS-04: Compiled code without SystemRequirements should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "void my_func(void) { }\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_system_requirements(pkg, desc)
        sys04 = [f for f in findings if f.rule_id == "SYS-04"]
        assert len(sys04) == 0

    # --- VIG-08: Custom Vignette Engine Bootstrap ---

    def test_vig08_self_referencing_builder(self, tmp_path):
        """VIG-08: VignetteBuilder listing the package itself should be flagged."""
        pkg = self._make_pkg(tmp_path, description_extra="VignetteBuilder: testpkg")
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{testpkg::custom}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "VIG-08" in rule_ids

    def test_vig08_builder_in_suggests_not_imports(self, tmp_path):
        """VIG-08: VignetteBuilder in Suggests but not Imports should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "VIG-08" in rule_ids

    def test_vig08_builder_in_imports_ok(self, tmp_path):
        """VIG-08: VignetteBuilder in Imports should NOT be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nImports: knitr\nSuggests: rmarkdown"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig08 = [f for f in findings if f.rule_id == "VIG-08"]
        assert len(vig08) == 0


# ============================================================================
# Severity constants test
# ============================================================================


class TestSeverityConstants:
    """Tests for severity ordering and lookup tables."""

    def test_severity_order(self):
        assert check.SEVERITY_ORDER["error"] < check.SEVERITY_ORDER["warning"]
        assert check.SEVERITY_ORDER["warning"] < check.SEVERITY_ORDER["note"]

    def test_severity_emoji(self):
        assert "error" in check.SEVERITY_EMOJI
        assert "warning" in check.SEVERITY_EMOJI
        assert "note" in check.SEVERITY_EMOJI

    def test_severity_gh(self):
        assert check.SEVERITY_GH["error"] == "error"
        assert check.SEVERITY_GH["warning"] == "warning"
        assert check.SEVERITY_GH["note"] == "notice"


# ============================================================================
# Heuristic Check Tests
# ============================================================================


class TestHeuristicChecks:
    """Tests for heuristic checks and informational reminders."""

    def _make_pkg(self, tmp_path, description_extra="", r_code="", rd_content="",
                  namespace_content="", has_news=True, has_cran_comments=True):
        """Helper to create a minimal synthetic package."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "R").mkdir()
        (pkg / "man").mkdir()

        desc_text = (
            "Package: testpkg\n"
            "Type: Package\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        if description_extra:
            desc_text += description_extra + "\n"
        (pkg / "DESCRIPTION").write_text(desc_text)
        (pkg / "LICENSE").write_text("YEAR: 2024\nCOPYRIGHT HOLDER: Test User\n")

        if namespace_content:
            (pkg / "NAMESPACE").write_text(namespace_content)
        else:
            (pkg / "NAMESPACE").write_text("export(test_fn)\n")

        if r_code:
            (pkg / "R" / "code.R").write_text(r_code)

        if rd_content:
            (pkg / "man" / "test.Rd").write_text(rd_content)

        if has_news:
            (pkg / "NEWS.md").write_text("# testpkg 0.1.0\n\n* Initial release.\n")
        if has_cran_comments:
            (pkg / "cran-comments.md").write_text("## R CMD check results\n\n0 errors | 0 warnings | 0 notes\n")

        return pkg

    # --- CODE-20: stringsAsFactors Compatibility ---

    def test_code20_strings_as_factors(self, tmp_path):
        """CODE-20: data.frame() + factor usage without stringsAsFactors should be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    df <- data.frame(name = x)\n"
            "    levels(df$name)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "CODE-20" in rule_ids

    def test_code20_with_strings_as_factors_ok(self, tmp_path):
        """CODE-20: data.frame() with stringsAsFactors should NOT be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    df <- data.frame(name = x, stringsAsFactors = FALSE)\n"
            "    levels(df$name)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code20 = [f for f in findings if f.rule_id == "CODE-20"]
        assert len(code20) == 0

    def test_code20_no_factor_usage_ok(self, tmp_path):
        """CODE-20: data.frame() without factor usage should NOT be flagged."""
        r_code = (
            "process_data <- function(x) {\n"
            "    df <- data.frame(name = x)\n"
            "    nrow(df)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        code20 = [f for f in findings if f.rule_id == "CODE-20"]
        assert len(code20) == 0

    # --- COMP-04: Implicit Function Declarations ---

    def test_comp04_missing_stdlib(self, tmp_path):
        """COMP-04: C file using malloc without stdlib.h should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "void my_func() {\n"
            "    void *p = malloc(100);\n"
            "    free(p);\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp04 = [f for f in findings if f.rule_id == "COMP-04"]
        assert len(comp04) >= 1
        assert any("stdlib.h" in f.message for f in comp04)

    def test_comp04_with_stdlib_ok(self, tmp_path):
        """COMP-04: C file using malloc with stdlib.h should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <stdlib.h>\n"
            "#include <R.h>\n"
            "void my_func() {\n"
            "    void *p = malloc(100);\n"
            "    free(p);\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp04 = [f for f in findings if f.rule_id == "COMP-04"]
        assert len(comp04) == 0

    def test_comp04_missing_string_h(self, tmp_path):
        """COMP-04: C file using strlen without string.h should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text(
            "#include <R.h>\n"
            "int my_func(const char *s) {\n"
            "    return strlen(s);\n"
            "}\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        comp04 = [f for f in findings if f.rule_id == "COMP-04"]
        assert len(comp04) >= 1
        assert any("string.h" in f.message for f in comp04)

    # --- DOC-03: Examples Must Be Fast ---

    def test_doc03_slow_example_sys_sleep(self, tmp_path):
        """DOC-03: Sys.sleep() in examples should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\examples{\n"
            "Sys.sleep(10)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-03" in rule_ids

    def test_doc03_slow_example_download(self, tmp_path):
        """DOC-03: download.file() in examples should be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\examples{\n"
            "download.file('http://example.com/data.csv', 'tmp.csv')\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        rule_ids = [f.rule_id for f in findings]
        assert "DOC-03" in rule_ids

    def test_doc03_fast_example_ok(self, tmp_path):
        """DOC-03: Simple examples should NOT be flagged."""
        rd_content = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
            "\\examples{\n"
            "x <- 1 + 1\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc03 = [f for f in findings if f.rule_id == "DOC-03"]
        assert len(doc03) == 0

    # --- DOC-04: Changes Go in .R Files, Not .Rd ---

    def test_doc04_hand_edited_rd_in_roxygen_project(self, tmp_path):
        """DOC-04: Hand-edited Rd file in roxygen project should be flagged."""
        rd_auto = (
            "% Generated by roxygen2: do not edit by hand\n"
            "\\name{auto_func}\n"
            "\\alias{auto_func}\n"
            "\\title{Auto Function}\n"
            "\\description{Auto generated.}\n"
        )
        rd_manual = (
            "\\name{manual_func}\n"
            "\\alias{manual_func}\n"
            "\\title{Manual Function}\n"
            "\\description{Hand edited.}\n"
        )
        pkg = self._make_pkg(tmp_path, description_extra="RoxygenNote: 7.3.1")
        (pkg / "man" / "auto_func.Rd").write_text(rd_auto)
        (pkg / "man" / "manual_func.Rd").write_text(rd_manual)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc04 = [f for f in findings if f.rule_id == "DOC-04"]
        assert len(doc04) >= 1
        assert any("manual_func.Rd" in f.title for f in doc04)

    def test_doc04_all_manual_rd_ok(self, tmp_path):
        """DOC-04: All-manual Rd files in roxygen project should NOT be flagged."""
        rd_manual = (
            "\\name{test}\n"
            "\\alias{test}\n"
            "\\title{Test}\n"
            "\\description{A test.}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_manual, description_extra="RoxygenNote: 7.3.1")
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc04 = [f for f in findings if f.rule_id == "DOC-04"]
        assert len(doc04) == 0

    # --- DOC-06: Function References Should Include Parentheses ---

    def test_doc06_function_ref_without_parens(self, tmp_path):
        """DOC-06: \\code{func} for exported function should be flagged."""
        rd_content = (
            "\\name{main_func}\n"
            "\\alias{main_func}\n"
            "\\title{Main Function}\n"
            "\\description{Uses \\code{test_fn} internally.}\n"
            "\\value{A value.}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc06 = [f for f in findings if f.rule_id == "DOC-06"]
        assert len(doc06) >= 1

    def test_doc06_function_ref_with_parens_ok(self, tmp_path):
        """DOC-06: \\code{func()} should NOT be flagged."""
        rd_content = (
            "\\name{main_func}\n"
            "\\alias{main_func}\n"
            "\\title{Main Function}\n"
            "\\description{Uses \\code{test_fn()} internally.}\n"
            "\\value{A value.}\n"
        )
        pkg = self._make_pkg(tmp_path, rd_content=rd_content)
        desc = check.parse_description(pkg)
        findings = check.check_documentation(pkg, desc)
        doc06 = [f for f in findings if f.rule_id == "DOC-06"]
        assert len(doc06) == 0

    # --- LIC-03: No Dual Licensing Within Package ---

    def test_lic03_mismatched_file_license(self, tmp_path):
        """LIC-03: File header mentioning different license should be flagged."""
        r_code = (
            "# Licensed under Apache License 2.0\n"
            "# Copyright 2024 Test Corp\n"
            "#\n"
            "test_fn <- function(x) x + 1\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        lic03 = [f for f in findings if f.rule_id == "LIC-03"]
        assert len(lic03) >= 1

    def test_lic03_matching_license_ok(self, tmp_path):
        """LIC-03: File header matching DESCRIPTION license should NOT be flagged."""
        r_code = (
            "# Licensed under MIT License\n"
            "# Copyright 2024 Test Corp\n"
            "#\n"
            "test_fn <- function(x) x + 1\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        lic03 = [f for f in findings if f.rule_id == "LIC-03"]
        assert len(lic03) == 0

    # --- PLAT-01: Must Work on Multiple Platforms ---

    def test_plat01_shell_call(self, tmp_path):
        """PLAT-01: shell() should be flagged as Windows-only."""
        r_code = (
            "run_command <- function(cmd) {\n"
            "    shell(cmd)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        plat01 = [f for f in findings if f.rule_id == "PLAT-01"]
        assert len(plat01) >= 1

    def test_plat01_cmd_call(self, tmp_path):
        """PLAT-01: system('cmd /c ...') should be flagged."""
        r_code = (
            "run_command <- function() {\n"
            '    system("cmd /c dir")\n'
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        plat01 = [f for f in findings if f.rule_id == "PLAT-01"]
        assert len(plat01) >= 1

    def test_plat01_system2_ok(self, tmp_path):
        """PLAT-01: system2() should NOT be flagged as platform-specific."""
        r_code = (
            "run_command <- function(cmd) {\n"
            "    system2(cmd, stdout = TRUE)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        plat01 = [f for f in findings if f.rule_id == "PLAT-01"]
        assert len(plat01) == 0

    # --- NET-03: Rate Limit Policy ---

    def test_net03_httr_usage(self, tmp_path):
        """NET-03: httr:: usage should emit rate limit reminder."""
        r_code = (
            "get_data <- function(url) {\n"
            "    tryCatch(httr::GET(url), error = function(e) NULL)\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        net03 = [f for f in findings if f.rule_id == "NET-03"]
        assert len(net03) >= 1

    def test_net03_no_network_code_ok(self, tmp_path):
        """NET-03: Package without network code should NOT emit NET-03."""
        r_code = (
            "add_numbers <- function(x, y) {\n"
            "    x + y\n"
            "}\n"
        )
        pkg = self._make_pkg(tmp_path, r_code=r_code)
        desc = check.parse_description(pkg)
        findings = check.check_code(pkg, desc)
        net03 = [f for f in findings if f.rule_id == "NET-03"]
        assert len(net03) == 0

    # --- VIG-06: Vignette Data Files in Wrong Location ---

    def test_vig06_relative_data_path(self, tmp_path):
        """VIG-06: Relative data path in vignette should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
            "```{r}\n"
            'df <- read.csv("../data/mydata.csv")\n'
            "```\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig06 = [f for f in findings if f.rule_id == "VIG-06"]
        assert len(vig06) >= 1

    def test_vig06_normal_path_ok(self, tmp_path):
        """VIG-06: Normal file reading without suspicious paths should NOT be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
            "```{r}\n"
            'df <- read.csv(system.file("extdata", "mydata.csv", package = "testpkg"))\n'
            "```\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig06 = [f for f in findings if f.rule_id == "VIG-06"]
        assert len(vig06) == 0

    # --- VIG-07: Vignette CPU Time ---

    def test_vig07_parallel_usage(self, tmp_path):
        """VIG-07: parallel:: in vignette should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown, parallel"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
            "```{r}\n"
            "parallel::mclapply(1:100, identity)\n"
            "```\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig07 = [f for f in findings if f.rule_id == "VIG-07"]
        assert len(vig07) >= 1

    def test_vig07_microbenchmark_usage(self, tmp_path):
        """VIG-07: microbenchmark in vignette should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown, microbenchmark"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "bench.Rmd").write_text(
            "---\ntitle: Benchmarks\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Benchmarks}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
            "```{r}\n"
            "microbenchmark(1 + 1)\n"
            "```\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig07 = [f for f in findings if f.rule_id == "VIG-07"]
        assert len(vig07) >= 1

    def test_vig07_simple_vignette_ok(self, tmp_path):
        """VIG-07: Simple vignette without heavy computation should NOT be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown"
        )
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\n"
            "```{r}\n"
            "x <- 1 + 1\n"
            "```\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_vignettes(pkg, desc)
        vig07 = [f for f in findings if f.rule_id == "VIG-07"]
        assert len(vig07) == 0


# ============================================================================
# Submission Readiness Tests
# ============================================================================


class TestSubmissionReadiness:
    """Tests for submission readiness informational reminders."""

    def _make_pkg(self, tmp_path, description_extra="", r_code="",
                  version="0.1.0", has_news=True, has_cran_comments=True):
        """Helper to create a minimal synthetic package."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "R").mkdir()
        (pkg / "man").mkdir()

        desc_text = (
            "Package: testpkg\n"
            "Type: Package\n"
            "Title: A Test Package for Unit Testing\n"
            f"Version: {version}\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: MIT + file LICENSE\n"
            "Encoding: UTF-8\n"
        )
        if description_extra:
            desc_text += description_extra + "\n"
        (pkg / "DESCRIPTION").write_text(desc_text)
        (pkg / "LICENSE").write_text("YEAR: 2024\nCOPYRIGHT HOLDER: Test User\n")
        (pkg / "NAMESPACE").write_text("export(test_fn)\n")

        if r_code:
            (pkg / "R" / "code.R").write_text(r_code)

        if has_news:
            (pkg / "NEWS.md").write_text(f"# testpkg {version}\n\n* Initial release.\n")
        if has_cran_comments:
            (pkg / "cran-comments.md").write_text("## R CMD check results\n\n0 errors | 0 warnings | 0 notes\n")

        return pkg

    # --- COMP-11: Memory Sanitizer Compliance ---

    def test_comp11_compiled_code(self, tmp_path):
        """COMP-11: Package with compiled code should emit sanitizer reminder."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text("#include <R.h>\nvoid my_func(void) { }\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        comp11 = [f for f in findings if f.rule_id == "COMP-11"]
        assert len(comp11) >= 1
        assert any("valgrind" in f.message.lower() or "ASAN" in f.message for f in comp11)

    def test_comp11_no_compiled_code_ok(self, tmp_path):
        """COMP-11: Package without compiled code should NOT emit COMP-11."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        comp11 = [f for f in findings if f.rule_id == "COMP-11"]
        assert len(comp11) == 0

    def test_comp11_cpp_code(self, tmp_path):
        """COMP-11: C++ code should also trigger COMP-11."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.cpp").write_text("// C++ code\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        comp11 = [f for f in findings if f.rule_id == "COMP-11"]
        assert len(comp11) >= 1

    def test_comp11_fortran_code(self, tmp_path):
        """COMP-11: Fortran code should also trigger COMP-11."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "src").mkdir()
        (pkg / "src" / "code.f").write_text("C Fortran code\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        comp11 = [f for f in findings if f.rule_id == "COMP-11"]
        assert len(comp11) >= 1

    # --- CODE-18: Do Not Remove Failing Tests ---

    def test_code18_empty_tests_dir(self, tmp_path):
        """CODE-18: Empty tests/ with many R files should be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "tests").mkdir()
        # Create 5+ R source files
        for i in range(6):
            (pkg / "R" / f"func{i}.R").write_text(f"func{i} <- function() {i}\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        code18 = [f for f in findings if f.rule_id == "CODE-18"]
        assert len(code18) >= 1

    def test_code18_tests_with_files_ok(self, tmp_path):
        """CODE-18: tests/ with test files should NOT be flagged."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "tests").mkdir()
        (pkg / "tests" / "testthat.R").write_text("library(testthat)\ntest_check('testpkg')\n")
        for i in range(6):
            (pkg / "R" / f"func{i}.R").write_text(f"func{i} <- function() {i}\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        code18 = [f for f in findings if f.rule_id == "CODE-18"]
        assert len(code18) == 0

    def test_code18_no_tests_dir_ok(self, tmp_path):
        """CODE-18: Package without tests/ should NOT be flagged for CODE-18."""
        pkg = self._make_pkg(tmp_path)
        for i in range(6):
            (pkg / "R" / f"func{i}.R").write_text(f"func{i} <- function() {i}\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        code18 = [f for f in findings if f.rule_id == "CODE-18"]
        assert len(code18) == 0

    # --- SIZE-02: Check Time Must Be Under 10 Minutes ---

    def test_size02_tests_vignettes_compiled(self, tmp_path):
        """SIZE-02: Package with tests + vignettes + compiled code should be flagged."""
        pkg = self._make_pkg(
            tmp_path,
            description_extra="VignetteBuilder: knitr\nSuggests: knitr, rmarkdown"
        )
        (pkg / "src").mkdir()
        (pkg / "src" / "code.c").write_text("#include <R.h>\nvoid my_func(void) { }\n")
        (pkg / "tests").mkdir()
        (pkg / "tests" / "test_basic.R").write_text("stopifnot(1 == 1)\n")
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n"
            "<!--\n"
            "%\\VignetteEngine{knitr::rmarkdown}\n"
            "%\\VignetteIndexEntry{Intro}\n"
            "%\\VignetteEncoding{UTF-8}\n"
            "-->\nHello\n"
        )
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        size02 = [f for f in findings if f.rule_id == "SIZE-02"]
        assert len(size02) >= 1

    def test_size02_tests_only_ok(self, tmp_path):
        """SIZE-02: Package with only tests should NOT be flagged for SIZE-02."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "tests").mkdir()
        (pkg / "tests" / "test_basic.R").write_text("stopifnot(1 == 1)\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        size02 = [f for f in findings if f.rule_id == "SIZE-02"]
        assert len(size02) == 0

    # --- SUB-01: Run R CMD check --as-cran ---

    def test_sub01_always_emitted(self, tmp_path):
        """SUB-01: Should always be emitted."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub01 = [f for f in findings if f.rule_id == "SUB-01"]
        assert len(sub01) == 1

    # --- SUB-02: Test on Multiple Platforms ---

    def test_sub02_always_emitted(self, tmp_path):
        """SUB-02: Should always be emitted."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub02 = [f for f in findings if f.rule_id == "SUB-02"]
        assert len(sub02) == 1

    # --- SUB-03: Check Reverse Dependencies ---

    def test_sub03_update_version(self, tmp_path):
        """SUB-03: Release version > 1.0.0 should emit reverse dep check reminder."""
        pkg = self._make_pkg(tmp_path, version="2.1.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub03 = [f for f in findings if f.rule_id == "SUB-03"]
        assert len(sub03) >= 1

    def test_sub03_first_release_ok(self, tmp_path):
        """SUB-03: First release (0.x) should NOT suggest reverse dep check."""
        pkg = self._make_pkg(tmp_path, version="0.1.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub03 = [f for f in findings if f.rule_id == "SUB-03"]
        assert len(sub03) == 0

    def test_sub03_version_1_0_0_ok(self, tmp_path):
        """SUB-03: Version 1.0.0 should NOT suggest reverse dep check."""
        pkg = self._make_pkg(tmp_path, version="1.0.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub03 = [f for f in findings if f.rule_id == "SUB-03"]
        assert len(sub03) == 0

    # --- SUB-05: First Submission Gets "New submission" NOTE ---

    def test_sub05_first_release(self, tmp_path):
        """SUB-05: Version 0.x should emit first submission note."""
        pkg = self._make_pkg(tmp_path, version="0.1.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub05 = [f for f in findings if f.rule_id == "SUB-05"]
        assert len(sub05) >= 1

    def test_sub05_version_100(self, tmp_path):
        """SUB-05: Version 1.0.0 should emit first submission note."""
        pkg = self._make_pkg(tmp_path, version="1.0.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub05 = [f for f in findings if f.rule_id == "SUB-05"]
        assert len(sub05) >= 1

    def test_sub05_later_version_ok(self, tmp_path):
        """SUB-05: Version 2.0.0 should NOT emit first submission note."""
        pkg = self._make_pkg(tmp_path, version="2.0.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub05 = [f for f in findings if f.rule_id == "SUB-05"]
        assert len(sub05) == 0

    # --- SUB-06: Submission Frequency Limit ---

    def test_sub06_always_emitted(self, tmp_path):
        """SUB-06: Should always be emitted."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        sub06 = [f for f in findings if f.rule_id == "SUB-06"]
        assert len(sub06) == 1

    # --- SUB-07: CRAN Vacation Periods ---

    def test_sub07_vacation_period(self, tmp_path):
        """SUB-07: Should emit during vacation months (Dec, Jul, Aug)."""
        from unittest.mock import patch
        import datetime

        # Mock today to be December 15
        mock_date = datetime.date(2025, 12, 15)
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        with patch("check.datetime") as mock_datetime:
            mock_datetime.date.today.return_value = mock_date
            mock_datetime.date.fromisoformat = datetime.date.fromisoformat
            findings = check.check_submission_readiness(pkg, desc)
        sub07 = [f for f in findings if f.rule_id == "SUB-07"]
        assert len(sub07) >= 1

    def test_sub07_non_vacation_period(self, tmp_path):
        """SUB-07: Should NOT emit during non-vacation months."""
        from unittest.mock import patch
        import datetime

        # Mock today to be March 15
        mock_date = datetime.date(2025, 3, 15)
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        with patch("check.datetime") as mock_datetime:
            mock_datetime.date.today.return_value = mock_date
            mock_datetime.date.fromisoformat = datetime.date.fromisoformat
            findings = check.check_submission_readiness(pkg, desc)
        sub07 = [f for f in findings if f.rule_id == "SUB-07"]
        assert len(sub07) == 0

    # --- NAME-02: Package Names Are Permanent ---

    def test_name02_first_release(self, tmp_path):
        """NAME-02: First release should warn about permanent names."""
        pkg = self._make_pkg(tmp_path, version="0.1.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        name02 = [f for f in findings if f.rule_id == "NAME-02"]
        assert len(name02) >= 1

    def test_name02_later_version_ok(self, tmp_path):
        """NAME-02: Later versions should NOT warn about names."""
        pkg = self._make_pkg(tmp_path, version="2.0.0")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        name02 = [f for f in findings if f.rule_id == "NAME-02"]
        assert len(name02) == 0

    # --- LIC-02: License Changes Must Be Highlighted ---

    def test_lic02_file_license(self, tmp_path):
        """LIC-02: License with 'file LICENSE' should emit reminder."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        lic02 = [f for f in findings if f.rule_id == "LIC-02"]
        assert len(lic02) >= 1

    def test_lic02_no_file_license_ok(self, tmp_path):
        """LIC-02: Standard license without file should NOT emit reminder."""
        pkg = self._make_pkg(tmp_path)
        # Overwrite with a license that doesn't use "file LICENSE"
        desc_text = (
            "Package: testpkg\n"
            "Title: A Test Package for Unit Testing\n"
            "Version: 0.1.0\n"
            'Authors@R: person("Test", "User", email = "test.user@gmail.com", role = c("aut", "cre", "cph"))\n'
            "Description: Provides test functionality for unit testing purposes.\n"
            "    This is a second sentence for the description field.\n"
            "License: GPL-3\n"
            "Encoding: UTF-8\n"
        )
        (pkg / "DESCRIPTION").write_text(desc_text)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        lic02 = [f for f in findings if f.rule_id == "LIC-02"]
        assert len(lic02) == 0

    # --- ENC-06: Unmarked UTF-8 Strings in Data ---

    def test_enc06_data_files(self, tmp_path):
        """ENC-06: Package with .rda data should emit encoding reminder."""
        pkg = self._make_pkg(tmp_path)
        (pkg / "data").mkdir()
        (pkg / "data" / "mydata.rda").write_bytes(b"\x00\x01\x02")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        enc06 = [f for f in findings if f.rule_id == "ENC-06"]
        assert len(enc06) >= 1

    def test_enc06_no_data_ok(self, tmp_path):
        """ENC-06: Package without data should NOT emit encoding reminder."""
        pkg = self._make_pkg(tmp_path)
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        enc06 = [f for f in findings if f.rule_id == "ENC-06"]
        assert len(enc06) == 0

    # --- NS-06: No Visible Binding Reminder ---

    def test_ns06_with_r_code(self, tmp_path):
        """NS-06: Package with R code should emit binding analysis reminder."""
        pkg = self._make_pkg(tmp_path, r_code="test_fn <- function() 42\n")
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        ns06 = [f for f in findings if f.rule_id == "NS-06"]
        assert len(ns06) >= 1

    def test_ns06_no_r_code_ok(self, tmp_path):
        """NS-06: Package without R/ files should NOT emit NS-06."""
        pkg = self._make_pkg(tmp_path)
        # Remove any R files
        for f in (pkg / "R").glob("*.R"):
            f.unlink()
        desc = check.parse_description(pkg)
        findings = check.check_submission_readiness(pkg, desc)
        ns06 = [f for f in findings if f.rule_id == "NS-06"]
        assert len(ns06) == 0


# ============================================================================
# Online checks tests
# ============================================================================


from unittest.mock import patch, MagicMock
import urllib.error


class TestOnlineChecksGating:
    """Tests that online checks are only run when --online is passed."""

    def test_online_checks_not_run_without_flag(self, clean_pkg):
        """Online check functions should not be called when --online is absent."""
        result = subprocess.run(
            [sys.executable, str(CHECK_PY), "--path", str(clean_pkg),
             "--severity", "note", "--fail-on", "error"],
            capture_output=True, text=True,
        )
        # Should not contain online-only rule IDs
        assert "MISC-02" not in result.stdout
        assert "MISC-07" not in result.stdout
        assert "MISC-03" not in result.stdout
        assert "DEP-03" not in result.stdout
        assert "NAME-01" not in result.stdout


class TestUrlCollection:
    """Tests for _collect_urls_from_files."""

    def test_urls_from_description(self, tmp_path):
        """URLs in DESCRIPTION URL and BugReports fields should be collected."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\n"
            "Title: Test\n"
            "Version: 0.1.0\n"
            "URL: https://example.com/pkg, https://github.com/user/pkg\n"
            "BugReports: https://github.com/user/pkg/issues\n"
        )
        urls = check._collect_urls_from_files(pkg, {})
        url_strs = [u[0] for u in urls]
        assert "https://example.com/pkg" in url_strs
        assert "https://github.com/user/pkg" in url_strs
        assert "https://github.com/user/pkg/issues" in url_strs

    def test_urls_from_rd_files(self, tmp_path):
        """URLs in .Rd files should be collected."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text("Package: testpkg\nTitle: Test\nVersion: 0.1.0\n")
        (pkg / "man").mkdir()
        (pkg / "man" / "foo.Rd").write_text(
            "\\name{foo}\n\\title{Foo}\n"
            "\\description{See \\url{https://example.com/docs}}\n"
        )
        urls = check._collect_urls_from_files(pkg, {})
        url_strs = [u[0] for u in urls]
        assert any("example.com/docs" in u for u in url_strs)

    def test_urls_from_readme(self, tmp_path):
        """URLs in README.md should be collected."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text("Package: testpkg\nTitle: Test\nVersion: 0.1.0\n")
        (pkg / "README.md").write_text(
            "# Test\n\nVisit https://example.com/readme for details.\n"
        )
        urls = check._collect_urls_from_files(pkg, {})
        url_strs = [u[0] for u in urls]
        assert any("example.com/readme" in u for u in url_strs)

    def test_urls_deduplicated(self, tmp_path):
        """Same URL appearing in multiple files should only appear once."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/dup\n"
        )
        (pkg / "README.md").write_text("Visit https://example.com/dup\n")
        urls = check._collect_urls_from_files(pkg, {})
        url_strs = [u[0] for u in urls]
        assert url_strs.count("https://example.com/dup") == 1

    def test_urls_from_vignettes(self, tmp_path):
        """URLs in vignette files should be collected."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text("Package: testpkg\nTitle: Test\nVersion: 0.1.0\n")
        (pkg / "vignettes").mkdir()
        (pkg / "vignettes" / "intro.Rmd").write_text(
            "---\ntitle: Intro\n---\n\nSee https://example.com/vignette\n"
        )
        urls = check._collect_urls_from_files(pkg, {})
        url_strs = [u[0] for u in urls]
        assert any("example.com/vignette" in u for u in url_strs)


class TestUrlValidationOnline:
    """Tests for check_urls_online with mocked network calls."""

    def test_broken_url_flagged(self, tmp_path):
        """MISC-02: 404 URL should produce a warning."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/broken\n"
        )
        with patch("check._http_head_no_redirect", return_value=(404, "")):
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        misc02 = [f for f in findings if f.rule_id == "MISC-02"]
        assert len(misc02) == 1
        assert misc02[0].severity == "warning"
        assert "404" in misc02[0].message

    def test_301_redirect_flagged(self, tmp_path):
        """MISC-07: 301 redirect should produce a note."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/old\n"
        )
        with patch("check._http_head_no_redirect", return_value=(301, "https://example.com/new")):
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        misc07 = [f for f in findings if f.rule_id == "MISC-07"]
        assert len(misc07) == 1
        assert misc07[0].severity == "note"
        assert "https://example.com/new" in misc07[0].message

    def test_200_ok_no_finding(self, tmp_path):
        """200 response should not produce any finding."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/good\n"
        )
        with patch("check._http_head_no_redirect", return_value=(200, "")):
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        assert len(findings) == 0

    def test_doi_urls_skipped(self, tmp_path):
        """DOI URLs should be skipped (they always redirect)."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://doi.org/10.1234/abc\n"
        )
        with patch("check._http_head_no_redirect") as mock_head:
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        mock_head.assert_not_called()
        assert len(findings) == 0

    def test_connection_error_handled_gracefully(self, tmp_path):
        """Connection errors should not crash the checker."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/timeout\n"
        )
        with patch("check._http_head_no_redirect", return_value=(-1, "Connection timed out")):
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        assert len(findings) == 0

    def test_500_server_error_flagged(self, tmp_path):
        """MISC-02: 500 server error should be flagged."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "DESCRIPTION").write_text(
            "Package: testpkg\nTitle: Test\nVersion: 0.1.0\n"
            "URL: https://example.com/error\n"
        )
        with patch("check._http_head_no_redirect", return_value=(500, "")):
            with patch("check.time.sleep"):
                findings = check.check_urls_online(pkg, {})
        misc02 = [f for f in findings if f.rule_id == "MISC-02"]
        assert len(misc02) == 1
        assert "500" in misc02[0].message


class TestSpellingOnline:
    """Tests for check_spelling_online with mocked aspell."""

    def test_aspell_not_found_gives_note(self):
        """MISC-03: When aspell is not found, a skip note should be emitted."""
        with patch("check.shutil.which", return_value=None):
            findings = check.check_spelling_online({"Title": "Hello World", "Description": "Some text."})
        assert len(findings) == 1
        assert findings[0].rule_id == "MISC-03"
        assert "aspell not found" in findings[0].title

    def test_aspell_finds_misspelling(self):
        """MISC-03: Misspelled words should be flagged."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "wrold\nmispeled\n"

        with patch("check.shutil.which", return_value="/usr/bin/aspell"):
            with patch("check.subprocess.run", return_value=mock_result):
                findings = check.check_spelling_online({
                    "Title": "A wrold of mispeled things",
                    "Description": "Some good text here. It is fine.",
                })
        misc03 = [f for f in findings if f.rule_id == "MISC-03"]
        assert len(misc03) >= 1
        assert "wrold" in misc03[0].message or "mispeled" in misc03[0].message

    def test_aspell_r_words_filtered(self):
        """MISC-03: R-ecosystem words should not be flagged as misspellings."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "dplyr\nggplot\nknitr\n"

        with patch("check.shutil.which", return_value="/usr/bin/aspell"):
            with patch("check.subprocess.run", return_value=mock_result):
                findings = check.check_spelling_online({
                    "Title": "Interface to dplyr and ggplot",
                    "Description": "Uses knitr for rendering. Another sentence here.",
                })
        misc03 = [f for f in findings if f.rule_id == "MISC-03"]
        assert len(misc03) == 0

    def test_aspell_no_misspellings_ok(self):
        """No findings when aspell finds no misspellings."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        with patch("check.shutil.which", return_value="/usr/bin/aspell"):
            with patch("check.subprocess.run", return_value=mock_result):
                findings = check.check_spelling_online({
                    "Title": "Proper English Title",
                    "Description": "This is correct. Two sentences here.",
                })
        misc03 = [f for f in findings if f.rule_id == "MISC-03"]
        assert len(misc03) == 0

    def test_aspell_timeout_handled(self):
        """Aspell timeout should be handled gracefully."""
        with patch("check.shutil.which", return_value="/usr/bin/aspell"):
            with patch("check.subprocess.run", side_effect=subprocess.TimeoutExpired("aspell", 10)):
                findings = check.check_spelling_online({
                    "Title": "Some Title",
                    "Description": "Some description. Another sentence.",
                })
        # Should not crash, may produce no findings
        assert isinstance(findings, list)


class TestDependencyParsingUnit:
    """Tests for _parse_dependency_packages helper."""

    def test_parse_depends_imports_linkingto(self):
        """Should extract packages from all three fields."""
        desc = {
            "Depends": "R (>= 3.5.0), dplyr, ggplot2",
            "Imports": "Rcpp (>= 1.0.0), rlang",
            "LinkingTo": "Rcpp",
        }
        pkgs = check._parse_dependency_packages(desc)
        assert "dplyr" in pkgs
        assert "ggplot2" in pkgs
        assert "Rcpp" in pkgs
        assert "rlang" in pkgs
        assert "R" not in pkgs  # Base R should be excluded

    def test_base_packages_excluded(self):
        """Base R packages should not be included."""
        desc = {
            "Depends": "R (>= 4.0.0), methods, stats, utils",
            "Imports": "grDevices, graphics",
        }
        pkgs = check._parse_dependency_packages(desc)
        assert len(pkgs) == 0

    def test_empty_fields(self):
        """Empty or missing fields should return empty list."""
        desc = {}
        pkgs = check._parse_dependency_packages(desc)
        assert pkgs == []


class TestDependenciesOnline:
    """Tests for check_dependencies_online with mocked network."""

    def test_dep01_missing_package_flagged(self):
        """DEP-01: Package not on CRAN or Bioconductor should be flagged as error."""
        desc = {"Imports": "nonexistentpkg123"}
        with patch("check._check_cran_package_exists", return_value=False):
            with patch("check._check_bioconductor_package_exists", return_value=False):
                with patch("check.time.sleep"):
                    findings = check.check_dependencies_online(desc)
        dep01 = [f for f in findings if f.rule_id == "DEP-01"]
        assert len(dep01) == 1
        assert dep01[0].severity == "error"
        assert "nonexistentpkg123" in dep01[0].message

    def test_dep01_cran_package_ok(self):
        """DEP-01: Package on CRAN should not be flagged for DEP-01."""
        desc = {"Imports": "ggplot2"}

        # Mock the CRAN check page to not have errors
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>OK OK OK</html>"
        mock_response.status = 200
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("check._check_cran_package_exists", return_value=True):
            with patch("check.urllib.request.urlopen", return_value=mock_response):
                with patch("check.time.sleep"):
                    findings = check.check_dependencies_online(desc)
        dep01 = [f for f in findings if f.rule_id == "DEP-01"]
        assert len(dep01) == 0

    def test_dep01_bioc_package_ok(self):
        """DEP-01: Package on Bioconductor should not be flagged."""
        desc = {"Imports": "BiocGenerics"}
        with patch("check._check_cran_package_exists", return_value=False):
            with patch("check._check_bioconductor_package_exists", return_value=True):
                with patch("check.time.sleep"):
                    findings = check.check_dependencies_online(desc)
        dep01 = [f for f in findings if f.rule_id == "DEP-01"]
        assert len(dep01) == 0

    def test_dep01_additional_repos_downgrades_to_note(self):
        """DEP-01: With Additional_repositories, missing pkg should be note, not error."""
        desc = {
            "Imports": "myprivatepkg",
            "Additional_repositories": "https://myrepo.example.com",
        }
        with patch("check._check_cran_package_exists", return_value=False):
            with patch("check._check_bioconductor_package_exists", return_value=False):
                with patch("check.time.sleep"):
                    findings = check.check_dependencies_online(desc)
        dep01 = [f for f in findings if f.rule_id == "DEP-01"]
        assert len(dep01) == 1
        assert dep01[0].severity == "note"

    def test_dep03_unhealthy_dependency(self):
        """DEP-03: Dependency with multiple CRAN check errors should be noted."""
        desc = {"Imports": "somepkg"}

        mock_response = MagicMock()
        mock_response.read.return_value = b"<td>ERROR</td><td>>ERROR<</td><td>>ERROR<</td><td>>ERROR<</td>"
        mock_response.status = 200
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("check._check_cran_package_exists", return_value=True):
            with patch("check.urllib.request.urlopen", return_value=mock_response):
                with patch("check.time.sleep"):
                    findings = check.check_dependencies_online(desc)
        dep03 = [f for f in findings if f.rule_id == "DEP-03"]
        assert len(dep03) == 1
        assert dep03[0].severity == "note"

    def test_connection_error_handled(self):
        """Network errors should not crash dependency checks."""
        desc = {"Imports": "somepkg"}
        with patch("check._check_cran_package_exists", side_effect=Exception("Network error")):
            with patch("check.time.sleep"):
                findings = check.check_dependencies_online(desc)
        assert isinstance(findings, list)


class TestPackageNameOnline:
    """Tests for check_package_name_online with mocked network."""

    def test_name01_existing_package_noted(self):
        """NAME-01: Existing package name on CRAN should produce a note."""
        desc = {"Package": "dplyr", "Version": "0.1.0"}
        with patch("check._check_cran_package_exists", return_value=True):
            findings = check.check_package_name_online(desc)
        name01 = [f for f in findings if f.rule_id == "NAME-01"]
        assert len(name01) == 1
        assert name01[0].severity == "note"
        assert "dplyr" in name01[0].message

    def test_name01_dev_version_existing_pkg(self):
        """NAME-01: Dev version of existing package gets specific message."""
        desc = {"Package": "dplyr", "Version": "1.1.0.9000"}
        with patch("check._check_cran_package_exists", return_value=True):
            findings = check.check_package_name_online(desc)
        name01 = [f for f in findings if f.rule_id == "NAME-01"]
        assert len(name01) == 1
        assert "development version" in name01[0].message

    def test_name01_new_name_ok(self):
        """NAME-01: Package name not on CRAN should produce no finding."""
        desc = {"Package": "totallyuniquename123xyz", "Version": "0.1.0"}
        with patch("check._check_cran_package_exists", return_value=False):
            findings = check.check_package_name_online(desc)
        assert len(findings) == 0

    def test_name01_empty_package_name(self):
        """NAME-01: Empty package name should produce no finding."""
        desc = {"Package": "", "Version": "0.1.0"}
        findings = check.check_package_name_online(desc)
        assert len(findings) == 0

    def test_name01_network_error_handled(self):
        """NAME-01: Network errors should not crash the check."""
        desc = {"Package": "somepkg", "Version": "0.1.0"}
        with patch("check._check_cran_package_exists", side_effect=Exception("Network error")):
            findings = check.check_package_name_online(desc)
        assert len(findings) == 0


class TestHttpHeadNoRedirect:
    """Tests for _http_head_no_redirect helper."""

    def test_connection_error_returns_negative_one(self):
        """Connection failures should return (-1, error_message)."""
        with patch("check.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.side_effect = Exception("Connection refused")
            status, msg = check._http_head_no_redirect("https://example.com/fail")
        assert status == -1
        assert "Connection refused" in msg

    def test_http_error_returns_status(self):
        """HTTP errors should return the status code."""
        error = urllib.error.HTTPError(
            url="https://example.com/gone",
            code=410,
            msg="Gone",
            hdrs=MagicMock(**{"get.return_value": ""}),
            fp=None,
        )
        with patch("check.urllib.request.build_opener") as mock_opener:
            mock_opener.return_value.open.side_effect = error
            status, location = check._http_head_no_redirect("https://example.com/gone")
        assert status == 410
