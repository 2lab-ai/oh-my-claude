#!/bin/bash
# Auto-title untitled Claude chats using claude-haiku-4-5
# Stop hook: reads session info from stdin, generates title if needed

# Read stop hook input from stdin
INPUT=$(cat)

# Extract transcript_path from JSON input
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty' 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ]; then
    exit 0
fi

# Expand ~ to home directory
TRANSCRIPT_PATH="${TRANSCRIPT_PATH/#\~/$HOME}"

if [ ! -f "$TRANSCRIPT_PATH" ]; then
    exit 0
fi

# Check if already has a summary (title) with ✦ marker
if head -1 "$TRANSCRIPT_PATH" | jq -e '.type == "summary"' >/dev/null 2>&1; then
    EXISTING_TITLE=$(head -1 "$TRANSCRIPT_PATH" | jq -r '.summary // empty')
    # Skip only if already has ✦ marker
    if echo "$EXISTING_TITLE" | grep -q '^✦'; then
        exit 0
    fi
    # Remove old title line to regenerate
    tail -n +2 "$TRANSCRIPT_PATH" > "$TRANSCRIPT_PATH.tmp" && mv "$TRANSCRIPT_PATH.tmp" "$TRANSCRIPT_PATH"
fi

# Extract first 4 messages (user + assistant, skip meta/commands)
MESSAGES=$(grep -E '"type":"(user|assistant)"' "$TRANSCRIPT_PATH" 2>/dev/null | \
    grep -v '"isMeta":true' | \
    grep -v '<command-name>' | \
    head -4 | \
    jq -r '.message.content // .message.content[0].text // empty' 2>/dev/null | \
    head -c 1500)

if [ -z "$MESSAGES" ] || [ ${#MESSAGES} -lt 5 ]; then
    exit 0
fi

# Get last message UUID for leafUuid
LAST_UUID=$(grep '"uuid"' "$TRANSCRIPT_PATH" | tail -1 | jq -r '.uuid // empty' 2>/dev/null)
if [ -z "$LAST_UUID" ]; then
    LAST_UUID=$(uuidgen 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "00000000-0000-0000-0000-000000000000")
fi

# Generate title using claude haiku (vanilla mode - no MCP)
# Use XML tags for reliable parsing
RESPONSE=$(claude -p --model haiku --no-session-persistence --strict-mcp-config "Generate a 3-5 word title for this conversation. Output in XML format: <title>YOUR TITLE HERE</title>

Conversation:
$MESSAGES" 2>/dev/null)

# Extract title from XML tags
TITLE=$(echo "$RESPONSE" | grep -oP '(?<=<title>).*?(?=</title>)' 2>/dev/null | head -1 | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -c 80)

# Fallback: try sed if grep -P not available
if [ -z "$TITLE" ]; then
    TITLE=$(echo "$RESPONSE" | sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' | head -1 | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -c 80)
fi

# Validate title
if [ -z "$TITLE" ] || [ "$TITLE" = "null" ] || [ ${#TITLE} -lt 3 ]; then
    exit 0
fi

# Add marker prefix to indicate auto-generated title
TITLE="✦ $TITLE"

# Create summary JSON line
SUMMARY_LINE=$(jq -cn --arg summary "$TITLE" --arg uuid "$LAST_UUID" '{type: "summary", summary: $summary, leafUuid: $uuid}')

# Prepend to file atomically
TEMP_FILE=$(mktemp)
echo "$SUMMARY_LINE" > "$TEMP_FILE"
cat "$TRANSCRIPT_PATH" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$TRANSCRIPT_PATH"

exit 0
