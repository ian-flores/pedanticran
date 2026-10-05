#!/bin/bash
set -e

# Pedantic CRAN — Install skills and knowledge base for Claude Code without the plugin system.
# Prefer: /plugin marketplace add ian-flores/pedanticran && /plugin install pedanticran@pedanticran
# Usage: ./install.sh [--global | --local]
#   --global: Install to ~/.claude/ (available in all projects)
#   --local:  Install to .claude/ in current directory (R package project)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---global}"

case "$MODE" in
  --global)
    TARGET="$HOME/.claude"
    echo "Installing Pedantic CRAN globally to $TARGET"
    ;;
  --local)
    if [ ! -f "DESCRIPTION" ]; then
      echo "Error: No DESCRIPTION file found. Run --local from an R package directory."
      exit 1
    fi
    TARGET=".claude"
    echo "Installing Pedantic CRAN locally to $TARGET"
    ;;
  *)
    echo "Usage: $0 [--global | --local]"
    exit 1
    ;;
esac

# Copy skills (one directory per skill, as Claude Code expects) and the knowledge base
for skill in cran-audit cran-fix cran-respond; do
  mkdir -p "$TARGET/skills/$skill"
  cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$TARGET/skills/$skill/"
done
mkdir -p "$TARGET/knowledge"
cp "$SCRIPT_DIR/knowledge/cran-rules.md" "$TARGET/knowledge/"

echo ""
echo "Installed:"
echo "  $TARGET/skills/cran-audit/SKILL.md"
echo "  $TARGET/skills/cran-fix/SKILL.md"
echo "  $TARGET/skills/cran-respond/SKILL.md"
echo "  $TARGET/knowledge/cran-rules.md"
echo ""
echo "Usage: Open Claude Code in an R package directory and run /cran-audit"
