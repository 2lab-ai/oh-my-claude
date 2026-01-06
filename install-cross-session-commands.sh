#!/bin/bash

# Install oh-my-claude cross-session commands to Gemini CLI and Codex
# Converts Claude .md commands to .toml (Gemini) and .md (Codex) formats

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_SRC="$SCRIPT_DIR/plugins/oh-my-claude/commands"
GEMINI_COMMANDS="$HOME/.gemini/commands"
CODEX_PROMPTS="$HOME/.codex/prompts"

# Commands to install (cross-session compatible)
COMMANDS=("save" "load" "list-saves" "check")

echo "=============================================="
echo "Installing oh-my-claude cross-session commands"
echo "=============================================="
echo ""
echo "Source: $COMMANDS_SRC"
echo ""

# ==================== Gemini CLI ====================
echo "--- Gemini CLI (~/.gemini/commands) ---"
mkdir -p "$GEMINI_COMMANDS"

for cmd in "${COMMANDS[@]}"; do
    md_path="$COMMANDS_SRC/${cmd}.md"
    toml_path="$GEMINI_COMMANDS/${cmd}.toml"

    if [ ! -f "$md_path" ]; then
        echo "  [SKIP] ${cmd}.md not found"
        continue
    fi

    python3 -c "
import re
import json

md_path = '$md_path'
toml_path = '$toml_path'

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

description = None
prompt = content

# Parse YAML frontmatter
match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
if match:
    frontmatter = match.group(1)
    prompt = match.group(2)

    for line in frontmatter.split('\n'):
        if line.strip().startswith('description:'):
            description = line.split(':', 1)[1].strip()
            if description.startswith('\"') and description.endswith('\"'):
                description = description[1:-1]
            elif description.startswith(\"'\") and description.endswith(\"'\"):
                description = description[1:-1]
            break

lines = []
if description:
    lines.append(f'description = {json.dumps(description)}')
lines.append(f'prompt = {json.dumps(prompt.strip())}')

with open(toml_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f'  [OK] $cmd.toml')
"
done

echo ""

# ==================== Codex ====================
echo "--- Codex (~/.codex/prompts) ---"
mkdir -p "$CODEX_PROMPTS"

for cmd in "${COMMANDS[@]}"; do
    md_path="$COMMANDS_SRC/${cmd}.md"
    codex_path="$CODEX_PROMPTS/${cmd}.md"

    if [ ! -f "$md_path" ]; then
        echo "  [SKIP] ${cmd}.md not found"
        continue
    fi

    # Codex uses .md files - strip Claude-specific frontmatter
    python3 -c "
import re

md_path = '$md_path'
codex_path = '$codex_path'

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse YAML frontmatter and extract just the prompt
match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
if match:
    prompt = match.group(2)
else:
    prompt = content

with open(codex_path, 'w', encoding='utf-8') as f:
    f.write(prompt.strip() + '\n')

print(f'  [OK] {codex_path.split(\"/\")[-1]}')
"
done

echo ""
echo "=============================================="
echo "Installation complete!"
echo "=============================================="
echo ""
echo "Cross-tool workflow:"
echo "  1. Save in Claude Code:  /save"
echo "  2. Load in Gemini CLI:   /load"
echo "  3. Load in Codex:        /load"
echo ""
echo "All tools share the same save location: ./docs/tasks/save/"
