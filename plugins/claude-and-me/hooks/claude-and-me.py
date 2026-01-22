#!/usr/bin/env python3
"""
Claude and Me - Session log archiver and format converter

Archives Claude session logs and converts them to human-readable formats.
- raw_logs/: Original JSONL backup (session ID based, append-only)
- chat_logs/: Converted chat logs (Markdown or JSON, incremental)

Features:
- Deduplication: Same session saves only new content
- Continuation support: Links to original when session spans dates
- Fork support: Links to parent session

Configuration: .claude/claude-and-me.json
{
  "raw_logs_dir": ".claude/raw_logs",
  "chat_logs_dir": ".claude/chat_logs",
  "chat_format": "md"  // "md" or "json"
}
"""
import sys
import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

LOG_FILE = Path("/tmp/claude-and-me.log")
CONFIG_FILE = ".claude/claude-and-me.json"

DEFAULT_CONFIG = {
    "raw_logs_dir": ".claude/raw_logs",
    "chat_logs_dir": ".claude/chat_logs",
    "chat_format": "md"
}


def log(msg: str) -> None:
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def load_config(project_dir: Path) -> dict:
    """Load configuration from .claude/claude-and-me.json"""
    config_path = project_dir / CONFIG_FILE
    config = DEFAULT_CONFIG.copy()

    if not config_path.exists():
        return config

    try:
        with open(config_path) as f:
            user_config = json.load(f)
            config.update(user_config)
            log(f"Config loaded from {config_path}")
    except (json.JSONDecodeError, IOError) as e:
        log(f"WARN: Failed to load config: {e}")

    return config


def get_output_config(transcript_path: Path) -> tuple[Path, Path, str]:
    """Determine output directories and format for logs"""
    project_dir_str = os.environ.get("CLAUDE_PROJECT_DIR")

    if not project_dir_str:
        log("WARN: CLAUDE_PROJECT_DIR not set, using fallback")
        project_name = transcript_path.parent.name
        fallback_dir = Path.home() / ".claude" / "session_logs" / project_name
        return (fallback_dir / "raw_logs", fallback_dir / "chat_logs", "md")

    project_dir = Path(project_dir_str)
    config = load_config(project_dir)

    raw_logs_path = Path(config["raw_logs_dir"])
    chat_logs_path = Path(config["chat_logs_dir"])
    chat_format = config.get("chat_format", "md")

    if not raw_logs_path.is_absolute():
        raw_logs_path = project_dir / raw_logs_path
    if not chat_logs_path.is_absolute():
        chat_logs_path = project_dir / chat_logs_path

    return (raw_logs_path, chat_logs_path, chat_format)


def find_files_by_pattern(base_dir: Path, pattern: str) -> list[Path]:
    """Find files matching pattern using find command. Returns empty list if none found."""
    if not base_dir.exists():
        return []

    try:
        result = subprocess.run(
            ["find", str(base_dir), "-name", pattern, "-type", "f"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [Path(f) for f in result.stdout.strip().split('\n')]
    except (subprocess.TimeoutExpired, OSError) as e:
        log(f"WARN: find command failed: {e}")

    return []


def find_existing_session_file(base_dir: Path, session_id: str, extension: str) -> Optional[Path]:
    """Find existing session file. Returns first match or None."""
    files = find_files_by_pattern(base_dir, f"*{session_id}{extension}")
    return files[0] if files else None


def find_all_session_files(base_dir: Path, session_id: str, extension: str) -> list[Path]:
    """Find all files for a session, sorted by date extracted from filename."""
    # Pattern: {session_id}.YYYY-MM-DD.HH_mm_ss{extension}
    files = find_files_by_pattern(base_dir, f"{session_id}.*{extension}")
    # Sort by date/time extracted from filename
    return sorted(files, key=lambda f: extract_datetime_from_filename(f.name, session_id))


def extract_datetime_from_filename(filename: str, session_id: str) -> str:
    """Extract date and time from filename for sorting.

    Filename format: {session_id}.YYYY-MM-DD.HH_mm_ss.md
    Returns: 'YYYY-MM-DD.HH_mm_ss' or empty string if not parseable
    """
    # Remove session_id prefix and extension
    prefix = f"{session_id}."
    if not filename.startswith(prefix):
        return ""

    rest = filename[len(prefix):]
    # Remove extension
    for ext in ['.md', '.json']:
        if rest.endswith(ext):
            rest = rest[:-len(ext)]
            break

    # rest should now be 'YYYY-MM-DD.HH_mm_ss'
    return rest


def get_summaries_cache_path(chat_logs_dir: Path, session_id: str) -> Path:
    """Get path to summaries cache file."""
    cache_dir = chat_logs_dir / ".summaries"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{session_id}.json"


def load_cached_summaries(cache_path: Path) -> dict[str, str]:
    """Load cached summaries from file. Returns empty dict if not found."""
    if not cache_path.exists():
        return {}

    try:
        with open(cache_path) as f:
            data = json.load(f)
            return data.get("summaries", {})
    except (json.JSONDecodeError, IOError) as e:
        log(f"WARN: Failed to load summaries cache: {e}")
        return {}


def save_cached_summaries(cache_path: Path, session_id: str, summaries: dict[str, str]) -> None:
    """Save summaries to cache file."""
    data = {
        "session_id": session_id,
        "summaries": summaries
    }
    try:
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        log(f"WARN: Failed to save summaries cache: {e}")


def generate_summary_via_cli(file_path: Path) -> str:
    """Generate a one-line summary using Claude Haiku via CLI.

    Returns summary string or 'Summary unavailable' on failure.
    Set CLAUDE_AND_ME_SKIP_SUMMARY=1 to skip actual CLI call (for testing).
    """
    # Skip in test mode
    if os.environ.get("CLAUDE_AND_ME_SKIP_SUMMARY"):
        return "Test summary"

    try:
        # Read first ~2000 chars of the file for summary
        content = file_path.read_text()[:2000]

        prompt = f"Summarize this conversation in ONE short sentence (max 50 chars). Just the summary, no quotes:\n\n{content}"

        result = subprocess.run(
            ["claude", "-p", "--model", "haiku", "--no-session-persistence", prompt],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            summary = result.stdout.strip()
            # Truncate if too long
            if len(summary) > 60:
                summary = summary[:57] + "..."
            return summary
    except (subprocess.TimeoutExpired, OSError, IOError) as e:
        log(f"WARN: Failed to generate summary: {e}")

    return "Summary unavailable"


def get_or_generate_summaries(chat_logs_dir: Path, session_id: str, files: list[Path]) -> dict[str, str]:
    """Get summaries for files, using cache when available and generating new ones.

    Returns dict mapping filename to summary.
    """
    cache_path = get_summaries_cache_path(chat_logs_dir, session_id)
    summaries = load_cached_summaries(cache_path)

    updated = False
    for file_path in files:
        filename = file_path.name
        if filename not in summaries:
            log(f"Generating summary for {filename}")
            summaries[filename] = generate_summary_via_cli(file_path)
            updated = True

    if updated:
        save_cached_summaries(cache_path, session_id, summaries)

    return summaries


def count_lines(file_path: Path) -> int:
    """Count lines in a file"""
    if not file_path.exists():
        return 0
    with open(file_path, 'r') as f:
        return sum(1 for _ in f)


def append_new_lines(source: Path, dest: Path, skip_lines: int) -> int:
    """Append only new lines from source to dest, return number of new lines"""
    new_lines = 0
    with open(source, 'r') as src:
        # Skip already-saved lines
        for _ in range(skip_lines):
            next(src, None)

        # Append new lines
        with open(dest, 'a') as dst:
            for line in src:
                dst.write(line)
                new_lines += 1

    return new_lines


def ensure_dir(dir_path: Path) -> None:
    """Create directory if not exists"""
    dir_path.mkdir(parents=True, exist_ok=True)


def save_raw_log(transcript_path: Path, raw_logs_dir: Path, session_id: str, date_str: str) -> tuple[Path, int, bool]:
    """
    Save raw JSONL log with deduplication.
    Returns: (file_path, new_lines_count, is_continuation)
    """
    # Find existing session file
    existing = find_existing_session_file(raw_logs_dir, session_id, ".jsonl")

    today_dir = raw_logs_dir / date_str
    ensure_dir(today_dir)
    dest_file = today_dir / f"{session_id}.jsonl"

    if existing:
        # Session continuation - move to today and append
        existing_lines = count_lines(existing)

        if existing != dest_file:
            # Move from old date to today
            shutil.move(str(existing), str(dest_file))
            log(f"Moved raw log from {existing} to {dest_file}")

        # Append only new lines
        new_lines = append_new_lines(transcript_path, dest_file, existing_lines)
        log(f"Appended {new_lines} new lines to {dest_file}")
        return (dest_file, new_lines, True)
    else:
        # New session - copy entire file
        shutil.copy2(transcript_path, dest_file)
        line_count = count_lines(dest_file)
        log(f"Created new raw log: {dest_file} ({line_count} lines)")
        return (dest_file, line_count, False)


def truncate_string(value: Any, max_length: int = 30) -> str:
    """Truncate any value to string with max length"""
    text = str(value)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def format_tool_signature(item: dict) -> str:
    """Convert tool_use to one-line signature for display."""
    name = item.get("name", "?")
    inputs = item.get("input", {})

    if not isinstance(inputs, dict) or not inputs:
        return f'{name}(...)'

    first_arg = next(iter(inputs.values()), "")
    return f'{name}("{truncate_string(first_arg)}")'


def extract_user_content(content: Any) -> str:
    """Extract user message content (string or list)"""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts)

    return ""


def parse_transcript(transcript_path: Path, skip_lines: int = 0) -> tuple[list[dict], Optional[str]]:
    """
    Parse JSONL transcript into structured conversation data.
    Returns: (messages, parent_session_id if forked)
    """
    messages = []
    parent_session_id = None

    with open(transcript_path) as f:
        for i, line in enumerate(f):
            if i < skip_lines:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Check for fork information in summary messages
            if msg.get("type") == "summary":
                parent_id = msg.get("parentSessionId") or msg.get("forkedFrom")
                if parent_id:
                    parent_session_id = parent_id

            msg_type = msg.get("type") or msg.get("message", {}).get("role")

            if msg_type == "user":
                content = msg.get("message", {}).get("content", "")
                text = extract_user_content(content)
                if text.strip():
                    messages.append({"role": "user", "content": text})

            elif msg_type == "assistant":
                content = msg.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue

                entry = {"role": "assistant", "content": [], "tools": []}

                for item in content:
                    item_type = item.get("type", "")
                    if item_type == "thinking":
                        thinking = item.get("thinking", "")
                        if thinking:
                            entry["content"].append({"type": "thinking", "text": thinking})
                    elif item_type == "text":
                        text = item.get("text", "")
                        if text:
                            entry["content"].append({"type": "text", "text": text})
                    elif item_type == "tool_use":
                        entry["tools"].append({
                            "name": item.get("name", "?"),
                            "input": item.get("input", {}),
                            "signature": format_tool_signature(item)
                        })

                if entry["content"] or entry["tools"]:
                    messages.append(entry)

    return (messages, parent_session_id)


def format_datetime_for_display(datetime_str: str) -> str:
    """Convert 'YYYY-MM-DD.HH_mm_ss' to 'YYYY-MM-DD HH:mm' for display."""
    # datetime_str is like '2026-01-22.10_30_00'
    if '.' in datetime_str:
        date_part, time_part = datetime_str.split('.', 1)
        # Convert HH_mm_ss to HH:mm
        time_display = time_part.replace('_', ':')[:5]
        return f"{date_part} {time_display}"
    return datetime_str


def format_markdown_header(session_id: str, now: datetime,
                           previous_files: Optional[list[Path]] = None,
                           summaries: Optional[dict[str, str]] = None,
                           is_fork: bool = False,
                           parent_session_id: Optional[str] = None,
                           current_dir: Optional[Path] = None) -> str:
    """Format markdown header with progressive history.

    Args:
        session_id: The session ID
        now: Current datetime
        previous_files: List of previous chat log files for this session (sorted by date)
        summaries: Dict mapping filename to summary (for 3rd+ saves)
        is_fork: Whether this is a forked session
        parent_session_id: Parent session ID if forked
        current_dir: Current directory for relative path calculation
    """
    date_time_str = now.strftime('%Y-%m-%d %H:%M')
    previous_files = previous_files or []
    summaries = summaries or {}

    # Fork handling (takes precedence)
    if is_fork and parent_session_id:
        return "\n".join([
            f"# Chat Log: {date_time_str} (Forked)",
            f"\n> **Forked from session**: `{parent_session_id}`",
            f"\nSession: `{session_id}`\n",
            "---\n"
        ])

    # Progressive headers based on previous file count
    num_previous = len(previous_files)

    if num_previous == 0:
        # 1st save: No reference
        ref_section = ""
    elif num_previous == 1:
        # 2nd save: Simple "Started from" link
        prev_file = previous_files[0]
        if current_dir:
            try:
                rel_path = os.path.relpath(prev_file, current_dir)
            except ValueError:
                rel_path = str(prev_file)
        else:
            rel_path = prev_file.name
        ref_section = f"\n> **Started from**: [{prev_file.name}]({rel_path})"
    else:
        # 3rd+ saves: History table
        table_lines = [
            "",
            "| No | Date | Link | Summary |",
            "|---|---|---|---|"
        ]
        for i, prev_file in enumerate(previous_files, 1):
            filename = prev_file.name
            dt_str = extract_datetime_from_filename(filename, session_id)
            display_date = format_datetime_for_display(dt_str)
            summary = summaries.get(filename, "")
            if current_dir:
                try:
                    rel_path = os.path.relpath(prev_file, current_dir)
                except ValueError:
                    rel_path = str(prev_file)
            else:
                rel_path = filename
            table_lines.append(f"| {i} | {display_date} | [{filename}]({rel_path}) | {summary} |")

        ref_section = "\n".join(table_lines)

    return "\n".join([
        f"# Chat Log: {date_time_str}",
        ref_section,
        f"\nSession: `{session_id}`\n",
        "---\n"
    ])


def format_markdown_messages(messages: list[dict]) -> str:
    """Format messages as Markdown"""
    lines = []

    for msg in messages:
        if msg["role"] == "user":
            lines.append(f"## User\n\n{msg['content']}\n\n---\n")

        elif msg["role"] == "assistant":
            lines.append("## Assistant\n")

            for item in msg.get("content", []):
                if item["type"] == "thinking":
                    lines.append(f"<details>\n<summary>Thinking</summary>\n\n{item['text']}\n\n</details>\n")
                elif item["type"] == "text":
                    lines.append(item["text"])

            tools = msg.get("tools", [])
            if tools:
                signatures = [t["signature"] for t in tools]
                lines.append(f"\n`{'` `'.join(signatures)}`\n")

            lines.append("\n---\n")

    return "\n".join(lines)


def format_json(messages: list[dict], session_id: str,
                is_continuation: bool = False,
                parent_session_id: Optional[str] = None) -> str:
    """Format parsed messages as JSON"""
    output = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "is_continuation": is_continuation,
        "messages": messages
    }
    if parent_session_id:
        output["forked_from"] = parent_session_id
    return json.dumps(output, indent=2, ensure_ascii=False)


def save_chat_log(transcript_path: Path, chat_logs_dir: Path, session_id: str,
                  chat_format: str, now: datetime, date_str: str, time_str: str,
                  raw_is_continuation: bool, raw_previous_lines: int,
                  parent_session_id: Optional[str] = None) -> Path:
    """Save chat log with progressive headers.

    Filename format: {session_id}.{date}.{time}.{extension}
    Progressive headers: 1st (none) -> 2nd (Started from) -> 3rd+ (history table)
    """
    extension = ".json" if chat_format == "json" else ".md"

    today_dir = chat_logs_dir / date_str
    ensure_dir(today_dir)

    # New filename format: {session_id}.YYYY-MM-DD.HH_mm_ss.md
    base_filename = f"{session_id}.{date_str}.{time_str}"
    chat_file = today_dir / f"{base_filename}{extension}"

    # Find all previous files for this session
    previous_files = find_all_session_files(chat_logs_dir, session_id, extension)

    is_fork = parent_session_id is not None

    # Determine what messages to include
    if raw_is_continuation and not is_fork:
        messages, _ = parse_transcript(transcript_path, skip_lines=raw_previous_lines)
        if not messages:
            log(f"No new messages to save for {session_id}")
            # Return most recent existing file if any
            return previous_files[-1] if previous_files else chat_file
    else:
        messages, detected_parent = parse_transcript(transcript_path)
        if not is_fork and detected_parent:
            parent_session_id = detected_parent
            is_fork = True  # Fork detected from transcript

    # Get summaries for 3rd+ saves (when there are 2+ previous files)
    summaries = {}
    if len(previous_files) >= 2 and chat_format != "json":
        summaries = get_or_generate_summaries(chat_logs_dir, session_id, previous_files)

    # Generate content
    if chat_format == "json":
        content = format_json(
            messages, session_id,
            is_continuation=len(previous_files) > 0,
            parent_session_id=parent_session_id if is_fork else None
        )
    else:
        header = format_markdown_header(
            session_id, now,
            previous_files=previous_files,
            summaries=summaries,
            is_fork=is_fork,
            parent_session_id=parent_session_id,
            current_dir=today_dir
        )
        content = header + format_markdown_messages(messages)

    with open(chat_file, "w") as f:
        f.write(content)

    num_prev = len(previous_files)
    log_msg = f"Created chat log: {chat_file} ({num_prev} previous)"
    log(log_msg)
    return chat_file


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        log("ERROR: Invalid JSON from stdin")
        return

    transcript_path_str = payload.get("transcript_path", "")
    if not transcript_path_str:
        log("SKIP: No transcript_path")
        return

    transcript_path = Path(transcript_path_str).expanduser()
    if not transcript_path.exists() or transcript_path.stat().st_size == 0:
        log(f"SKIP: File not found or empty: {transcript_path}")
        return

    raw_logs_dir, chat_logs_dir, chat_format = get_output_config(transcript_path)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H_%M_%S")
    session_id = transcript_path.stem

    # Save raw log (with deduplication)
    raw_file, new_lines, is_continuation = save_raw_log(
        transcript_path, raw_logs_dir, session_id, date_str
    )

    # Calculate previous line count for chat log parsing
    total_lines = count_lines(transcript_path)
    previous_lines = total_lines - new_lines if is_continuation else 0

    # Check for fork (from hook payload if available)
    parent_session_id = payload.get("parent_session_id") or payload.get("forked_from")

    # Save chat log (with deduplication and continuation support)
    chat_file = save_chat_log(
        transcript_path, chat_logs_dir, session_id, chat_format,
        now, date_str, time_str,
        is_continuation, previous_lines,
        parent_session_id
    )

    log(f"Session {session_id}: raw={raw_file}, chat={chat_file}, cont={is_continuation}")


if __name__ == "__main__":
    main()
