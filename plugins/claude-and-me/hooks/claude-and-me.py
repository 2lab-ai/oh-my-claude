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


def format_markdown_header(session_id: str, now: datetime,
                           is_continuation: bool = False,
                           original_file: Optional[str] = None,
                           is_fork: bool = False,
                           parent_session_id: Optional[str] = None) -> str:
    """Format markdown header with continuation/fork info"""
    date_time_str = now.strftime('%Y-%m-%d %H:%M')

    # Determine header type suffix and reference line
    if is_fork and parent_session_id:
        title_suffix = " (Forked)"
        ref_line = f"\n> **Forked from session**: `{parent_session_id}`"
    elif is_continuation and original_file:
        title_suffix = " (Continued)"
        ref_line = f"\n> **Continued from**: [{original_file}]({original_file})"
    else:
        title_suffix = ""
        ref_line = ""

    return "\n".join([
        f"# Chat Log: {date_time_str}{title_suffix}",
        ref_line,
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


def find_original_chat_log(chat_logs_dir: Path, session_id: str, extension: str) -> Optional[Path]:
    """Find the original (first) chat log for this session, excluding _cont files."""
    files = find_files_by_pattern(chat_logs_dir, f"*{session_id}{extension}")
    for f in files:
        if "_cont" not in f.stem:
            return f
    return None


def save_chat_log(transcript_path: Path, chat_logs_dir: Path, session_id: str,
                  chat_format: str, now: datetime, date_str: str, time_str: str,
                  raw_is_continuation: bool, raw_previous_lines: int,
                  parent_session_id: Optional[str] = None) -> Path:
    """Save chat log with deduplication and continuation support."""
    extension = ".json" if chat_format == "json" else ".md"
    existing = find_existing_session_file(chat_logs_dir, session_id, extension)

    today_dir = chat_logs_dir / date_str
    ensure_dir(today_dir)

    base_filename = f"{date_str}.{time_str}.{session_id}"
    is_fork = parent_session_id is not None
    is_continuation = existing and not is_fork

    if is_continuation:
        messages, _ = parse_transcript(transcript_path, skip_lines=raw_previous_lines)
        if not messages:
            log(f"No new messages to save for {session_id}")
            return existing

        chat_file = today_dir / f"{base_filename}_cont{extension}"
        try:
            original_relative = os.path.relpath(existing, today_dir)
        except ValueError:
            original_relative = str(existing)

        if chat_format == "json":
            content = format_json(messages, session_id, is_continuation=True)
        else:
            header = format_markdown_header(session_id, now, is_continuation=True, original_file=original_relative)
            content = header + format_markdown_messages(messages)

        log_msg = f"Created continuation chat log: {chat_file}"
    else:
        chat_file = today_dir / f"{base_filename}{extension}"
        messages, detected_parent = parse_transcript(transcript_path)
        parent_id = parent_session_id or detected_parent

        if chat_format == "json":
            content = format_json(messages, session_id, parent_session_id=parent_id)
        else:
            header = format_markdown_header(session_id, now, is_fork=bool(parent_id), parent_session_id=parent_id)
            content = header + format_markdown_messages(messages)

        log_msg = f"Created new chat log: {chat_file}"

    with open(chat_file, "w") as f:
        f.write(content)

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
    time_str = now.strftime("%H-%M")
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
