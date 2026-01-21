#!/usr/bin/env python3
"""
Claude and Me - Session log archiver and format converter

Archives Claude session logs and converts them to human-readable formats.
- raw_logs/: Original JSONL backup
- chat_logs/: Converted chat logs (Markdown or JSON)

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
from pathlib import Path
from datetime import datetime
from typing import Any

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


def ensure_dirs(raw_dir: Path, chat_dir: Path, date_str: str) -> None:
    """Create output directories"""
    (raw_dir / date_str).mkdir(parents=True, exist_ok=True)
    (chat_dir / date_str).mkdir(parents=True, exist_ok=True)


def copy_raw(transcript_path: Path, raw_dir: Path, base_name: str) -> Path:
    """Copy original JSONL file"""
    dest = raw_dir / f"{base_name}.jsonl"
    if dest.exists():
        dest = raw_dir / f"{base_name}_{os.getpid()}.jsonl"
    shutil.copy2(transcript_path, dest)
    return dest


def truncate_string(value: Any, max_length: int = 30) -> str:
    """Truncate any value to string with max length"""
    text = str(value)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def parse_tool_call(item: dict) -> str:
    """Convert tool_use to one-line signature"""
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


def parse_transcript(transcript_path: Path) -> list[dict]:
    """Parse JSONL transcript into structured conversation data"""
    messages = []

    with open(transcript_path) as f:
        for line in f:
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

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
                            "signature": parse_tool_call(item)
                        })

                if entry["content"] or entry["tools"]:
                    messages.append(entry)

    return messages


def format_markdown(messages: list[dict], session_id: str) -> str:
    """Format parsed messages as Markdown"""
    lines = [
        f"# Chat Log: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\nSession: `{session_id}`\n",
        "---\n"
    ]

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


def format_json(messages: list[dict], session_id: str) -> str:
    """Format parsed messages as JSON"""
    output = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    return json.dumps(output, indent=2, ensure_ascii=False)


def convert_transcript(transcript_path: Path, chat_file: Path, session_id: str, chat_format: str) -> None:
    """Convert JSONL transcript to specified format"""
    messages = parse_transcript(transcript_path)

    if chat_format == "json":
        content = format_json(messages, session_id)
    else:
        content = format_markdown(messages, session_id)

    with open(chat_file, "w") as f:
        f.write(content)


def get_unique_path(base_path: Path) -> Path:
    """Return unique path by appending PID if file exists"""
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    return base_path.parent / f"{stem}_{os.getpid()}{suffix}"


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
    time_str = now.strftime("%H-%M-%S")
    session_id = transcript_path.stem
    base_name = f"{time_str}_{session_id}"

    ensure_dirs(raw_logs_dir, chat_logs_dir, date_str)

    raw_dir = raw_logs_dir / date_str
    chat_dir = chat_logs_dir / date_str

    # Copy raw JSONL
    raw_file = copy_raw(transcript_path, raw_dir, base_name)
    log(f"Raw copied: {raw_file}")

    # Convert to configured format
    extension = ".json" if chat_format == "json" else ".md"
    chat_file = get_unique_path(chat_dir / f"{base_name}{extension}")
    convert_transcript(transcript_path, chat_file, session_id, chat_format)
    log(f"Chat converted: {chat_file}")


if __name__ == "__main__":
    main()
