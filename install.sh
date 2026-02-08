#!/bin/bash
set -e

# Pedantic CRAN — Install skills and knowledge base for Claude Code
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

# Create directories
mkdir -p "$TARGET/skills"
mkdir -p "$TARGET/knowledge"

# Copy files
cp "$SCRIPT_DIR/skills/cran-audit.md" "$TARGET/skills/"
cp "$SCRIPT_DIR/skills/cran-fix.md" "$TARGET/skills/"
cp "$SCRIPT_DIR/knowledge/cran-rules.md" "$TARGET/knowledge/"

# Register skill trigger in skill-rules.json (if it exists and cran-audit isn't already there)
RULES_FILE="$TARGET/skills/skill-rules.json"
if [ -f "$RULES_FILE" ] && ! grep -q '"cran-audit"' "$RULES_FILE"; then
  echo "Registering cran-audit trigger in skill-rules.json..."
  # Use a temp file to inject the cran-audit entry
  python3 -c "
import json, sys
with open('$RULES_FILE') as f:
    data = json.load(f)
data['skills']['cran-fix'] = {
    'type': 'domain',
    'enforcement': 'suggest',
    'priority': 'high',
    'description': 'Auto-fix CRAN submission issues in an R package',
    'promptTriggers': {
        'keywords': ['cran fix', 'fix cran', 'cran-fix', 'auto-fix cran', 'prepare for cran', 'make cran ready'],
        'intentPatterns': ['(fix|remediate|prepare|auto.?fix).*?cran', 'cran.*?(fix|ready|prepare)', 'make.*?cran.*?ready']
    }
}
data['skills']['cran-audit'] = {
    'type': 'domain',
    'enforcement': 'suggest',
    'priority': 'high',
    'description': 'Audit R package for CRAN submission readiness',
    'promptTriggers': {
        'keywords': ['cran', 'cran audit', 'cran check', 'cran submission', 'submit to cran', 'cran readiness', 'prepare for cran', 'pedantic check', 'cran-audit'],
        'intentPatterns': ['(audit|check|prepare|ready).*?cran', 'cran.*?(audit|check|submission|ready)', '(submit|submitting).*?cran', 'pedantic.*?check']
    }
}
with open('$RULES_FILE', 'w') as f:
    json.dump(data, f, indent=4)
print('  Registered cran-audit in skill-rules.json')
" 2>/dev/null || echo "  (Skipped skill-rules.json registration — add manually if needed)"
fi

echo ""
echo "Installed:"
echo "  $TARGET/skills/cran-audit.md"
echo "  $TARGET/skills/cran-fix.md"
echo "  $TARGET/knowledge/cran-rules.md"
echo ""
echo "Usage: Open Claude Code in an R package directory and run /cran-audit"
