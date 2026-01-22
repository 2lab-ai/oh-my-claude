# claude-and-me Specification

## Overview

Claude session log archiver and format converter plugin for Claude Code.

- **raw_logs/**: Original JSONL backup (session ID based, append-only)
- **chat_logs/**: Converted chat logs (Markdown or JSON, incremental)

## Features

| Feature | Description |
|---------|-------------|
| Deduplication | Same session saves only new content (no duplicates) |
| Continuation | Links to original when session spans multiple dates |
| Fork Support | Links to parent session when forked |
| Date Boundary | Handles date/year changes correctly |

## File Structure

### raw_logs

```
.claude/raw_logs/
└── {YYYY-MM-DD}/
    └── {session_id}.jsonl
```

- **Naming**: `{session_id}.jsonl` (no timestamp prefix)
- **Behavior**:
  - New session: Copy entire transcript
  - Continuation: Find existing file → Move to today's date → Append new lines only
- **Deduplication**: Line count comparison, append only new lines

### chat_logs

```
.claude/chat_logs/
└── {YYYY-MM-DD}/
    └── {session_id}.YYYY-MM-DD.HH_mm_ss.md
```

- **Naming**: `{session_id}.{date}.{time}.{extension}` (session_id first for easier searching)
- **Format**: Markdown (default) or JSON
- **No continuation suffix**: Each save creates a new timestamped file

## Behavior Details

### Progressive Headers

Headers evolve based on how many times a session has been saved:

**1st save (new session):**
```markdown
# Chat Log: 2026-01-22 10:30

Session: `abc-123-def`

---
```

**2nd save (one previous):**
```markdown
# Chat Log: 2026-01-22 14:00

> **Started from**: [abc-123-def.2026-01-22.10_30_00.md](link)

Session: `abc-123-def`

---
```

**3rd+ saves (history table):**
```markdown
# Chat Log: 2026-01-22 18:00

| No | Date | Link | Summary |
|---|---|---|---|
| 1 | 2026-01-22 10:30 | [link](path) | Initial setup |
| 2 | 2026-01-22 14:00 | [link](path) | Added auth |

Session: `abc-123-def`

---
```

### Summary Generation

For 3rd+ saves, optionally generates a one-line summary for each previous conversation:
- **Disabled by default** - set `summary_model` in config to enable
- Models: `haiku`, `sonnet`, or `opus`
- CLI: `claude -p --model {summary_model} --no-session-persistence "Summarize: ..."`
- Fallback: "Summary unavailable" if model fails
- Cache: `.claude/chat_logs/.summaries/{session_id}.json`

Cache structure:
```json
{
  "session_id": "abc-123",
  "summaries": {
    "abc-123.2026-01-22.10_30_00.md": "Initial project setup",
    "abc-123.2026-01-22.14_00_00.md": "Added authentication"
  }
}
```

### 1. New Session

- raw_logs: Copy entire transcript
- chat_logs: Create file with basic header (no references)

### 2. Continued Session

When a session is resumed:
- raw_logs: Append new lines to existing file (move to today if needed)
- chat_logs: Create new timestamped file with progressive header

### 3. Forked Session

When a session is forked (new session ID from parent):
- raw_logs: New file (independent from parent)
- chat_logs: New file with parent session reference

```markdown
# Chat Log: 2026-01-22 10:30 (Forked)

> **Forked from session**: `parent-session-id`

Session: `new-forked-session-id`

---
```

Fork detection:
1. Hook payload: `parent_session_id` or `forked_from` field
2. Transcript: `summary` message with `parentSessionId` or `forkedFrom`

## Configuration

File: `.claude/claude-and-me.json`

```json
{
  "raw_logs_dir": ".claude/raw_logs",
  "chat_logs_dir": ".claude/chat_logs",
  "chat_format": "md",
  "summary_model": null
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `raw_logs_dir` | `.claude/raw_logs` | Directory for raw JSONL logs |
| `chat_logs_dir` | `.claude/chat_logs` | Directory for converted chat logs |
| `chat_format` | `md` | Output format: `md` or `json` |
| `summary_model` | `null` | Model for summaries: `haiku`, `sonnet`, `opus`, or `null` (disabled) |

## Hook Configuration

File: `hooks/hooks.json`

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/claude-and-me.py"
          }
        ]
      }
    ]
  }
}
```

## Implementation Details

### Session File Discovery

Uses `find` command to search for existing session files:

```bash
find {base_dir} -name "*{session_id}.jsonl" -type "f"
```

### Deduplication Algorithm

1. Find existing session file (if any)
2. Count lines in existing file
3. Skip that many lines from source transcript
4. Append only remaining (new) lines

```python
existing_lines = count_lines(existing_file)
new_lines = append_new_lines(source, dest, skip_lines=existing_lines)
```

### Chat Log Parsing

Only parse new lines for continuation:

```python
messages, parent_id, seen_uuids = parse_transcript(transcript_path, skip_lines=previous_line_count)
```

### UUID Deduplication

Claude Code transcript files may contain duplicate messages with the same UUID. The parser skips messages with already-seen UUIDs to prevent duplication in chat logs.

### Message Formatting

**Consecutive Assistant Messages**: Merged into a single `## Assistant` block until a User message appears.

**Thinking Content**: Uses `<thinking>` tags (not `<details>`) for readability.

**Item Order**: Preserves original order of thinking, text, and tool calls from the API response.

Example output:
```markdown
## User

Do something for me.

---

## Assistant

<thinking>
User wants me to do something...
</thinking>

Let me help with that.

`Read("/path/to/file")`

`Edit("/path/to/file")`

Done! I've made the changes.

---
```

Key formatting rules:
- One `## Assistant` header per continuous response block
- Tool calls shown inline as backtick code
- `---` separator only after User messages and at the end of Assistant blocks

## Log File

Debug logs: `/tmp/claude-and-me.log`

```
[2026-01-22T10:30:00.000000] Created new raw log: .claude/raw_logs/2026-01-22/abc-123.jsonl (42 lines)
[2026-01-22T10:30:00.000000] Created new chat log: .claude/chat_logs/2026-01-22/abc-123.2026-01-22.10_30_00.md
[2026-01-22T14:00:00.000000] Appended 10 new lines to .claude/raw_logs/2026-01-22/abc-123.jsonl
[2026-01-22T14:00:00.000000] Created chat log: .claude/chat_logs/2026-01-22/abc-123.2026-01-22.14_00_00.md (1 previous)
```

## Search Sessions

To find all logs for a session:

```bash
# Find raw log
find .claude/raw_logs -name "*{session_id}.jsonl"

# Find all chat logs for session
find .claude/chat_logs -name "{session_id}*.md"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.3.0 | 2026-01-23 | Fix duplicate messages by UUID deduplication |
| 3.2.0 | 2026-01-22 | Make summary generation optional via `summary_model` config |
| 3.1.0 | 2026-01-22 | Merge consecutive assistant messages, use `<thinking>` tags |
| 3.0.0 | 2026-01-22 | New filename format, progressive headers, Haiku summaries |
| 2.0.0 | 2026-01-22 | Session ID based storage, deduplication, continuation links, fork support |
| 1.0.0 | Initial | Basic session archiving with timestamp-based files |
