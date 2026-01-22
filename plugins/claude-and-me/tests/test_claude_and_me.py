#!/usr/bin/env python3
"""
Tests for claude-and-me plugin.

Tests the SessionEnd hook behavior by simulating actual hook calls
with subprocess, verifying spec compliance.

Run: uv run --with pytest pytest plugins/claude-and-me/tests/test_claude_and_me.py -v
"""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Generator, Optional
from unittest.mock import patch, MagicMock

import pytest


SCRIPT_PATH = Path(__file__).parent.parent / "hooks" / "claude-and-me.py"


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace with proper directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Create .claude directory for config
        claude_dir = workspace / ".claude"
        claude_dir.mkdir()

        # Create config file
        config = {
            "raw_logs_dir": ".claude/raw_logs",
            "chat_logs_dir": ".claude/chat_logs",
            "chat_format": "md"
        }
        with open(claude_dir / "claude-and-me.json", "w") as f:
            json.dump(config, f)

        yield workspace


def create_transcript(path: Path, messages: list[dict]) -> None:
    """Create a JSONL transcript file."""
    with open(path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")


def append_transcript(path: Path, messages: list[dict]) -> None:
    """Append messages to existing transcript."""
    with open(path, "a") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")


def call_hook(transcript_path: Path, project_dir: Path, extra_payload: Optional[dict] = None) -> subprocess.CompletedProcess:
    """Call claude-and-me.py like SessionEnd hook does."""
    payload = {"transcript_path": str(transcript_path)}
    if extra_payload:
        payload.update(extra_payload)

    env = {
        **os.environ,
        "CLAUDE_PROJECT_DIR": str(project_dir),
        "CLAUDE_AND_ME_SKIP_SUMMARY": "1"  # Skip actual Haiku calls in tests
    }

    return subprocess.run(
        ["python3", str(SCRIPT_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=10
    )


def count_lines(path: Path) -> int:
    """Count lines in a file."""
    return sum(1 for _ in open(path)) if path.exists() else 0


def find_files(base_dir: Path, pattern: str) -> list[Path]:
    """Find files matching pattern using glob."""
    return list(base_dir.rglob(pattern))


class TestNewSession:
    """Test Case 1: New session creation."""

    def test_creates_raw_log_with_session_id(self, temp_workspace: Path):
        """raw_logs should create {session_id}.jsonl file."""
        session_id = "new-session-abc123"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "Hello"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Hi!"}]}}
        ]
        create_transcript(transcript, messages)

        call_hook(transcript, temp_workspace)

        # Check raw_logs
        raw_files = find_files(temp_workspace / ".claude" / "raw_logs", f"*{session_id}.jsonl")
        assert len(raw_files) == 1, f"Expected 1 raw log file, found {len(raw_files)}"
        assert raw_files[0].name == f"{session_id}.jsonl"
        assert count_lines(raw_files[0]) == 2

    def test_creates_chat_log_with_correct_format(self, temp_workspace: Path):
        """chat_logs should create {session_id}.YYYY-MM-DD.HH_mm_ss.md file."""
        session_id = "new-session-def456"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "Test message"}}
        ]
        create_transcript(transcript, messages)

        call_hook(transcript, temp_workspace)

        # Check chat_logs - new format: {session_id}.YYYY-MM-DD.HH_mm_ss.md
        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        assert len(chat_files) == 1

        # Verify filename format: {session_id}.YYYY-MM-DD.HH_mm_ss.md
        filename = chat_files[0].name
        parts = filename.replace(".md", "").split(".")
        assert len(parts) == 3, f"Expected format session_id.YYYY-MM-DD.HH_mm_ss, got {filename}"
        assert parts[0] == session_id
        assert len(parts[1]) == 10  # YYYY-MM-DD
        assert len(parts[2]) == 8   # HH_mm_ss

    def test_chat_log_contains_session_header(self, temp_workspace: Path):
        """Chat log should have proper header with session ID (no references for 1st save)."""
        session_id = "header-test-session"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "Hello"}}
        ]
        create_transcript(transcript, messages)

        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        content = chat_files[0].read_text()

        assert "# Chat Log:" in content
        assert f"Session: `{session_id}`" in content
        # First save should NOT have any reference
        assert "Started from" not in content
        assert "(Forked)" not in content


class TestContinuationSameDate:
    """Test Case 2: Session continuation (progressive headers)."""

    def test_raw_log_appends_only_new_lines(self, temp_workspace: Path):
        """raw_logs should append only new lines, not duplicate."""
        session_id = "continuation-test-123"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # First session
        messages1 = [
            {"type": "user", "message": {"role": "user", "content": "First message"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "First response"}]}}
        ]
        create_transcript(transcript, messages1)
        call_hook(transcript, temp_workspace)

        raw_files = find_files(temp_workspace / ".claude" / "raw_logs", f"*{session_id}.jsonl")
        initial_lines = count_lines(raw_files[0])
        assert initial_lines == 2

        # Continuation
        messages2 = [
            {"type": "user", "message": {"role": "user", "content": "Second message"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Second response"}]}}
        ]
        append_transcript(transcript, messages2)
        call_hook(transcript, temp_workspace)

        # Should have 4 lines total (not 6 from duplication)
        raw_files = find_files(temp_workspace / ".claude" / "raw_logs", f"*{session_id}.jsonl")
        assert len(raw_files) == 1, "Should still be single file"
        final_lines = count_lines(raw_files[0])
        assert final_lines == 4, f"Expected 4 lines (2+2), got {final_lines}"

    def test_second_save_creates_new_file_with_started_from(self, temp_workspace: Path):
        """2nd save should create new file with 'Started from' header."""
        session_id = "second-save-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # First session
        messages1 = [{"type": "user", "message": {"role": "user", "content": "First"}}]
        create_transcript(transcript, messages1)
        call_hook(transcript, temp_workspace)

        # Wait to ensure different timestamp
        time.sleep(1.1)

        # Continuation
        messages2 = [{"type": "user", "message": {"role": "user", "content": "Second"}}]
        append_transcript(transcript, messages2)
        call_hook(transcript, temp_workspace)

        # Should have 2 separate files (no _cont suffix)
        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        assert len(chat_files) == 2, f"Expected 2 chat files, found {len(chat_files)}"

        # Neither file should have _cont
        for f in chat_files:
            assert "_cont" not in f.name, f"File should not have _cont: {f.name}"

    def test_second_save_has_started_from_header(self, temp_workspace: Path):
        """2nd save should have 'Started from' in header."""
        session_id = "started-from-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # First + continuation
        create_transcript(transcript, [{"type": "user", "message": {"role": "user", "content": "First"}}])
        call_hook(transcript, temp_workspace)

        # Wait to ensure different timestamp
        time.sleep(1.1)

        append_transcript(transcript, [{"type": "user", "message": {"role": "user", "content": "Second"}}])
        call_hook(transcript, temp_workspace)

        # Find the second file (most recent)
        chat_files = sorted(find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md"))
        second_file = chat_files[-1]  # Latest by name
        content = second_file.read_text()

        assert "**Started from**:" in content
        # Should link to first file
        first_file = chat_files[0]
        assert first_file.name in content

    def test_third_save_has_history_table(self, temp_workspace: Path):
        """3rd+ save should have history table with all previous files."""
        session_id = "history-table-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # First session
        create_transcript(transcript, [{"type": "user", "message": {"role": "user", "content": "First"}}])
        call_hook(transcript, temp_workspace)

        # Wait to ensure different timestamp
        time.sleep(1.1)

        # Second session
        append_transcript(transcript, [{"type": "user", "message": {"role": "user", "content": "Second"}}])
        call_hook(transcript, temp_workspace)

        # Wait to ensure different timestamp
        time.sleep(1.1)

        # Third session
        append_transcript(transcript, [{"type": "user", "message": {"role": "user", "content": "Third"}}])
        call_hook(transcript, temp_workspace)

        # Find the third file (most recent)
        chat_files = sorted(find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md"))
        assert len(chat_files) == 3, f"Expected 3 chat files, found {len(chat_files)}"

        third_file = chat_files[-1]
        content = third_file.read_text()

        # Should have history table, not "Started from"
        assert "| No | Date | Link | Summary |" in content
        assert "| 1 |" in content
        assert "| 2 |" in content
        # Should NOT have "Started from" (that's only for 2nd save)
        assert "**Started from**" not in content


class TestDateBoundary:
    """Test Case 3 & 4: Date and year boundary handling."""

    def test_raw_log_moves_to_new_date(self, temp_workspace: Path):
        """raw_log should move from old date to new date on continuation."""
        session_id = "date-boundary-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # Manually create old date structure
        old_date = "2025-12-31"
        old_raw_dir = temp_workspace / ".claude" / "raw_logs" / old_date
        old_raw_dir.mkdir(parents=True)

        old_raw_file = old_raw_dir / f"{session_id}.jsonl"
        create_transcript(old_raw_file, [
            {"type": "user", "message": {"role": "user", "content": "Old message"}}
        ])

        # Create transcript with more content
        create_transcript(transcript, [
            {"type": "user", "message": {"role": "user", "content": "Old message"}},
            {"type": "user", "message": {"role": "user", "content": "New message"}}
        ])

        call_hook(transcript, temp_workspace)

        # Old file should be gone
        assert not old_raw_file.exists(), "Old raw file should be moved"

        # New file should exist in today's date
        raw_files = find_files(temp_workspace / ".claude" / "raw_logs", f"*{session_id}.jsonl")
        assert len(raw_files) == 1
        assert old_date not in str(raw_files[0]), "File should not be in old date directory"

    def test_chat_log_has_relative_path_for_cross_date(self, temp_workspace: Path):
        """Continuation across dates should use relative path with ../"""
        session_id = "cross-date-link-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # Create old chat log with new filename format
        old_date = "2025-12-31"
        old_chat_dir = temp_workspace / ".claude" / "chat_logs" / old_date
        old_chat_dir.mkdir(parents=True)

        old_chat_file = old_chat_dir / f"{session_id}.{old_date}.23_59_00.md"
        old_chat_file.write_text(f"# Chat Log\n\nSession: `{session_id}`\n")

        # Also create old raw log
        old_raw_dir = temp_workspace / ".claude" / "raw_logs" / old_date
        old_raw_dir.mkdir(parents=True)
        old_raw_file = old_raw_dir / f"{session_id}.jsonl"
        create_transcript(old_raw_file, [{"type": "user", "message": {"role": "user", "content": "Old"}}])

        # Create continuation transcript
        create_transcript(transcript, [
            {"type": "user", "message": {"role": "user", "content": "Old"}},
            {"type": "user", "message": {"role": "user", "content": "New"}}
        ])

        call_hook(transcript, temp_workspace)

        # Find continuation file (in today's directory)
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        today_files = find_files(temp_workspace / ".claude" / "chat_logs" / today, f"{session_id}.*.md")
        assert len(today_files) >= 1, "Should have file in today's directory"

        content = today_files[0].read_text()
        # Should reference the old file with relative path
        assert "../" in content or old_chat_file.name in content, f"Should reference old file"


class TestForkSession:
    """Test Case 5: Forked session handling."""

    def test_fork_creates_new_file(self, temp_workspace: Path):
        """Forked session should create independent files."""
        parent_id = "parent-session-abc"
        fork_id = "forked-session-xyz"

        fork_transcript = temp_workspace / f"{fork_id}.jsonl"
        create_transcript(fork_transcript, [
            {"type": "summary", "parentSessionId": parent_id},
            {"type": "user", "message": {"role": "user", "content": "Forked content"}}
        ])

        call_hook(fork_transcript, temp_workspace, {"parent_session_id": parent_id})

        # Should create files with fork_id, not parent_id
        raw_files = find_files(temp_workspace / ".claude" / "raw_logs", f"*{fork_id}.jsonl")
        assert len(raw_files) == 1

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{fork_id}.*.md")
        assert len(chat_files) == 1

    def test_fork_has_forked_header(self, temp_workspace: Path):
        """Forked session should have (Forked) in header."""
        parent_id = "parent-abc"
        fork_id = "fork-xyz"

        fork_transcript = temp_workspace / f"{fork_id}.jsonl"
        create_transcript(fork_transcript, [
            {"type": "user", "message": {"role": "user", "content": "Content"}}
        ])

        call_hook(fork_transcript, temp_workspace, {"parent_session_id": parent_id})

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{fork_id}.*.md")
        content = chat_files[0].read_text()

        assert "(Forked)" in content
        assert f"**Forked from session**: `{parent_id}`" in content

    def test_fork_detected_from_transcript(self, temp_workspace: Path):
        """Fork should be detected from transcript summary message."""
        parent_id = "detected-parent"
        fork_id = "detected-fork"

        fork_transcript = temp_workspace / f"{fork_id}.jsonl"
        create_transcript(fork_transcript, [
            {"type": "summary", "parentSessionId": parent_id},
            {"type": "user", "message": {"role": "user", "content": "Content"}}
        ])

        # No parent_session_id in payload - should detect from transcript
        call_hook(fork_transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{fork_id}.*.md")
        content = chat_files[0].read_text()

        assert "(Forked)" in content
        assert parent_id in content


class TestNoNewMessages:
    """Test Case 6: No new messages in continuation."""

    def test_no_new_file_when_no_new_messages(self, temp_workspace: Path):
        """Should not create new file if no new messages."""
        session_id = "no-new-messages-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [{"type": "user", "message": {"role": "user", "content": "Only message"}}]
        create_transcript(transcript, messages)
        call_hook(transcript, temp_workspace)

        # Call again with same content (no new messages)
        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        # Should only have original file
        assert len(chat_files) == 1, f"Expected 1 file (no new file), found {len(chat_files)}"


class TestJsonFormat:
    """Test JSON output format."""

    def test_json_format_creates_json_file(self, temp_workspace: Path):
        """Should create .json file when format is json."""
        session_id = "json-format-test"

        # Update config for JSON format
        config_path = temp_workspace / ".claude" / "claude-and-me.json"
        with open(config_path, "w") as f:
            json.dump({
                "raw_logs_dir": ".claude/raw_logs",
                "chat_logs_dir": ".claude/chat_logs",
                "chat_format": "json"
            }, f)

        transcript = temp_workspace / f"{session_id}.jsonl"
        create_transcript(transcript, [
            {"type": "user", "message": {"role": "user", "content": "Test"}}
        ])

        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.json")
        assert len(chat_files) == 1

        # Verify it's valid JSON
        content = json.loads(chat_files[0].read_text())
        assert content["session_id"] == session_id
        assert "messages" in content


class TestMessageFormatting:
    """Test message formatting with merged assistant blocks and <thinking> tags."""

    def test_consecutive_assistant_messages_merged(self, temp_workspace: Path):
        """Consecutive assistant messages should be merged into single block."""
        session_id = "merge-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        # Multiple consecutive assistant messages (typical tool use pattern)
        messages = [
            {"type": "user", "message": {"role": "user", "content": "Do something"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Let me help."}]}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Read", "input": {"path": "/test"}}]}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Done!"}]}},
        ]
        create_transcript(transcript, messages)
        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        content = chat_files[0].read_text()

        # Should have only ONE "## Assistant" header (merged)
        assert content.count("## Assistant") == 1, f"Expected 1 assistant header, got {content.count('## Assistant')}"

    def test_thinking_uses_thinking_tag(self, temp_workspace: Path):
        """Thinking content should use <thinking> tag, not <details>."""
        session_id = "thinking-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "Think"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "Deep thoughts here"},
                {"type": "text", "text": "Response"}
            ]}},
        ]
        create_transcript(transcript, messages)
        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        content = chat_files[0].read_text()

        # Should use <thinking> tag
        assert "<thinking>" in content
        assert "</thinking>" in content
        assert "Deep thoughts here" in content
        # Should NOT use <details>
        assert "<details>" not in content
        assert "<summary>" not in content

    def test_items_preserve_order(self, temp_workspace: Path):
        """Items should appear in original order: thinking, text, tool, text."""
        session_id = "order-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "Question"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "THINK_FIRST"},
                {"type": "text", "text": "TEXT_SECOND"},
                {"type": "tool_use", "name": "Tool", "input": {"a": "TOOL_THIRD"}},
                {"type": "text", "text": "TEXT_FOURTH"}
            ]}},
        ]
        create_transcript(transcript, messages)
        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        content = chat_files[0].read_text()

        # Verify order
        idx_think = content.find("THINK_FIRST")
        idx_text2 = content.find("TEXT_SECOND")
        idx_tool = content.find("TOOL_THIRD")
        idx_text4 = content.find("TEXT_FOURTH")

        assert idx_think < idx_text2 < idx_tool < idx_text4, "Items should be in original order"

    def test_user_message_separates_assistant_blocks(self, temp_workspace: Path):
        """User message between assistants should create separate blocks."""
        session_id = "separate-test"
        transcript = temp_workspace / f"{session_id}.jsonl"

        messages = [
            {"type": "user", "message": {"role": "user", "content": "First question"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "First answer"}]}},
            {"type": "user", "message": {"role": "user", "content": "Second question"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Second answer"}]}},
        ]
        create_transcript(transcript, messages)
        call_hook(transcript, temp_workspace)

        chat_files = find_files(temp_workspace / ".claude" / "chat_logs", f"{session_id}.*.md")
        content = chat_files[0].read_text()

        # Should have TWO "## Assistant" headers (separated by user)
        assert content.count("## Assistant") == 2


class TestHelperFunctions:
    """Test helper functions directly."""

    def test_extract_datetime_from_filename(self):
        """Test datetime extraction from new filename format."""
        import sys
        sys.path.insert(0, str(SCRIPT_PATH.parent))
        from importlib import import_module
        import importlib.util
        spec = importlib.util.spec_from_file_location("claude_and_me", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test normal case
        result = module.extract_datetime_from_filename(
            "abc-123.2026-01-22.10_30_00.md", "abc-123"
        )
        assert result == "2026-01-22.10_30_00"

        # Test with json extension
        result = module.extract_datetime_from_filename(
            "abc-123.2026-01-22.10_30_00.json", "abc-123"
        )
        assert result == "2026-01-22.10_30_00"

        # Test non-matching session id
        result = module.extract_datetime_from_filename(
            "other-session.2026-01-22.10_30_00.md", "abc-123"
        )
        assert result == ""

    def test_format_datetime_for_display(self):
        """Test datetime formatting for display."""
        import sys
        sys.path.insert(0, str(SCRIPT_PATH.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("claude_and_me", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.format_datetime_for_display("2026-01-22.10_30_00")
        assert result == "2026-01-22 10:30"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
