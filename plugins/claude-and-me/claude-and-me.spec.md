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
    ├── YYYY-MM-DD.HH-mm.{session_id}.md        # First session
    └── YYYY-MM-DD.HH-mm.{session_id}_cont.md   # Continuation
```

- **Naming**: `{date}.{time}.{session_id}.md`
- **Continuation suffix**: `_cont`
- **Format**: Markdown (default) or JSON

## Behavior Details

### 1. New Session

```markdown
# Chat Log: 2026-01-22 10:30

Session: `abc-123-def`

---

## User

Hello!

---

## Assistant

Hi there!

---
```

### 2. Continued Session (Same Date)

When a session is resumed on the same date:
- raw_logs: Append new lines to existing file
- chat_logs: Create new `_cont` file with link

```markdown
# Chat Log: 2026-01-22 14:00 (Continued)

> **Continued from**: [2026-01-22.10-30.abc-123-def.md](2026-01-22.10-30.abc-123-def.md)

Session: `abc-123-def`

---

## User

(Only new messages from this continuation)

---
```

### 3. Continued Session (Different Date/Year)

When a session spans dates (including year boundaries):
- raw_logs: Move file from old date to new date, then append
- chat_logs: Create continuation file with relative path link

```markdown
# Chat Log: 2026-01-01 00:05 (Continued)

> **Continued from**: [../2025-12-31/2025-12-31.23-59.abc-123-def.md](../2025-12-31/2025-12-31.23-59.abc-123-def.md)

Session: `abc-123-def`

---
```

### 4. Forked Session

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
  "chat_format": "md"
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `raw_logs_dir` | `.claude/raw_logs` | Directory for raw JSONL logs |
| `chat_logs_dir` | `.claude/chat_logs` | Directory for converted chat logs |
| `chat_format` | `md` | Output format: `md` or `json` |

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
messages, parent_id = parse_transcript(transcript_path, skip_lines=previous_line_count)
```

## Log File

Debug logs: `/tmp/claude-and-me.log`

```
[2026-01-22T10:30:00.000000] Created new raw log: .claude/raw_logs/2026-01-22/abc-123.jsonl (42 lines)
[2026-01-22T10:30:00.000000] Created new chat log: .claude/chat_logs/2026-01-22/2026-01-22.10-30.abc-123.md
[2026-01-22T14:00:00.000000] Appended 10 new lines to .claude/raw_logs/2026-01-22/abc-123.jsonl
[2026-01-22T14:00:00.000000] Created continuation chat log: .claude/chat_logs/2026-01-22/2026-01-22.14-00.abc-123_cont.md
```

## Search Sessions

To find all logs for a session:

```bash
# Find raw log
find .claude/raw_logs -name "*{session_id}.jsonl"

# Find all chat logs (original + continuations)
find .claude/chat_logs -name "*{session_id}*.md"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-22 | Session ID based storage, deduplication, continuation links, fork support |
| 1.0.0 | Initial | Basic session archiving with timestamp-based files |
