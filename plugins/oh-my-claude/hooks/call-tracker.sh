#!/bin/bash
# Call Tracker - Auto-logs agent/MCP calls with real timestamps
# Usage: call-tracker.sh <pre|post|report|reset|list>
#
# For pre/post: reads hook input JSON from stdin (includes session_id)
# Session-aware: Uses session_id from Claude Code hook input
# Parallel-safe: Each call gets unique state file

ACTION="$1"

LOG_DIR="/tmp/claude-calls"
mkdir -p "$LOG_DIR"

# Read stdin JSON for pre/post actions (Claude Code passes hook input via stdin)
read_hook_input() {
  if [[ -t 0 ]]; then
    # No stdin (interactive mode or manual call)
    HOOK_INPUT="{}"
  else
    HOOK_INPUT=$(cat)
  fi
}

# Extract session_id from hook input, fallback to generated ID
get_session_id() {
  local sid
  sid=$(echo "$HOOK_INPUT" | jq -r '.session_id // empty' 2>/dev/null)
  if [[ -z "$sid" ]]; then
    # Fallback: use env var or generate
    sid="${CLAUDE_SESSION_ID:-$(date '+%Y%m%d_%H%M%S')_$$}"
  fi
  echo "$sid"
}

# Extract tool_name from hook input
get_tool_name() {
  echo "$HOOK_INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null
}

# Extract description from tool_input
get_description() {
  local tool_name="$1"
  local desc
  if [[ "$tool_name" == "Task" ]]; then
    desc=$(echo "$HOOK_INPUT" | jq -r '.tool_input.description // "agent call"' 2>/dev/null)
  else
    desc=$(echo "$tool_name" | sed 's/mcp__plugin_oh-my-claude_//' | sed 's/__/:/g')
  fi
  echo "$desc"
}

# Only track Task and MCP calls
should_track() {
  local tool_name="$1"
  case "$tool_name" in
    Task|mcp__*) return 0 ;;
    *) return 1 ;;
  esac
}

case "$ACTION" in
  pre)
    read_hook_input

    TOOL_NAME=$(get_tool_name)
    if ! should_track "$TOOL_NAME"; then exit 0; fi

    SESSION_ID=$(get_session_id)
    LOG_FILE="$LOG_DIR/session_${SESSION_ID}.log"
    SESSION_META="$LOG_DIR/session_${SESSION_ID}.meta"

    TIMESTAMP=$(date '+%H:%M:%S')
    EPOCH=$(date '+%s')
    DESC=$(get_description "$TOOL_NAME")

    # Initialize session meta if first call
    if [[ ! -f "$SESSION_META" ]]; then
      echo "{\"start\":\"$(date '+%Y-%m-%d %H:%M:%S')\",\"start_epoch\":$EPOCH,\"session_id\":\"$SESSION_ID\"}" > "$SESSION_META"
    fi

    # Store state with unique call ID (RANDOM for parallel uniqueness)
    STATE_FILE="$LOG_DIR/state_${SESSION_ID}_${TOOL_NAME}_${EPOCH}_${RANDOM}_$$.json"
    echo "{\"tool\":\"$TOOL_NAME\",\"desc\":\"$DESC\",\"start\":\"$TIMESTAMP\",\"epoch\":$EPOCH}" > "$STATE_FILE"
    ;;

  post)
    read_hook_input

    TOOL_NAME=$(get_tool_name)
    if ! should_track "$TOOL_NAME"; then exit 0; fi

    SESSION_ID=$(get_session_id)
    LOG_FILE="$LOG_DIR/session_${SESSION_ID}.log"

    TIMESTAMP=$(date '+%H:%M:%S')
    EPOCH=$(date '+%s')

    # Find the state file for this tool (FIFO - oldest first for parallel calls)
    FOUND_STATE=$(ls -tr "$LOG_DIR"/state_${SESSION_ID}_${TOOL_NAME}_*.json 2>/dev/null | head -1)

    if [[ -f "$FOUND_STATE" ]]; then
      START_TIME=$(jq -r '.start' "$FOUND_STATE" 2>/dev/null)
      START_EPOCH=$(jq -r '.epoch' "$FOUND_STATE" 2>/dev/null)
      DESC=$(jq -r '.desc' "$FOUND_STATE" 2>/dev/null)
      DURATION=$((EPOCH - START_EPOCH))

      # Determine status from tool_response if available
      TOOL_RESPONSE=$(echo "$HOOK_INPUT" | jq -r '.tool_response // empty' 2>/dev/null)
      if echo "$TOOL_RESPONSE" | grep -qi "error\|fail\|timeout"; then
        STATUS="error"
      else
        STATUS="ok"
      fi

      # Get next sequence number (mkdir-based lock for macOS)
      LOCK_FILE="$LOG_FILE.lock"
      while ! mkdir "$LOCK_FILE" 2>/dev/null; do sleep 0.01; done
      trap "rmdir '$LOCK_FILE' 2>/dev/null" EXIT

      if [[ -f "$LOG_FILE" ]]; then
        SEQ=$(( $(wc -l < "$LOG_FILE") + 1 ))
      else
        SEQ=1
      fi
      echo "$SEQ|$TOOL_NAME|$DESC|$START_TIME|$TIMESTAMP|${DURATION}s|$STATUS" >> "$LOG_FILE"

      rmdir "$LOCK_FILE" 2>/dev/null
      rm -f "$FOUND_STATE"
    fi
    ;;

  start)
    # Mark tracking start point for current session
    # Subsequent 'report' will only show calls after this marker
    SESSION_ARG="$2"
    if [[ -n "$SESSION_ARG" ]]; then
      LOG_FILE="$LOG_DIR/session_${SESSION_ARG}.log"
      SESSION_ID="$SESSION_ARG"
    else
      LOG_FILE=$(ls -t "$LOG_DIR"/session_*.log 2>/dev/null | head -1)
      SESSION_ID=$(basename "$LOG_FILE" 2>/dev/null | sed 's/session_//' | sed 's/\.log//')
    fi

    MARKER_FILE="$LOG_DIR/session_${SESSION_ID}.start_marker"

    if [[ -f "$LOG_FILE" ]]; then
      # Mark current line count as start point
      CURRENT_LINE=$(wc -l < "$LOG_FILE" | tr -d ' ')
    else
      CURRENT_LINE=0
    fi

    echo "$CURRENT_LINE" > "$MARKER_FILE"
    echo "Tracking started at line $CURRENT_LINE for session $SESSION_ID"
    echo "Subsequent 'report' will only show calls after this point."
    ;;

  report)
    # Find session log (use provided session or most recent)
    SESSION_ARG="$2"
    if [[ -n "$SESSION_ARG" ]]; then
      LOG_FILE="$LOG_DIR/session_${SESSION_ARG}.log"
      SESSION_META="$LOG_DIR/session_${SESSION_ARG}.meta"
      SESSION_ID="$SESSION_ARG"
    else
      LOG_FILE=$(ls -t "$LOG_DIR"/session_*.log 2>/dev/null | head -1)
      SESSION_META=$(echo "$LOG_FILE" | sed 's/\.log$/.meta/')
      SESSION_ID=$(basename "$LOG_FILE" 2>/dev/null | sed 's/session_//' | sed 's/\.log//')
    fi

    if [[ ! -f "$LOG_FILE" ]]; then
      echo "No calls logged for session."
      exit 0
    fi

    # Check for start marker
    MARKER_FILE="$LOG_DIR/session_${SESSION_ID}.start_marker"
    if [[ -f "$MARKER_FILE" ]]; then
      START_LINE=$(cat "$MARKER_FILE")
      MARKER_TIME=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$MARKER_FILE" 2>/dev/null || stat -c '%y' "$MARKER_FILE" 2>/dev/null | cut -d'.' -f1)
    else
      START_LINE=0
      MARKER_TIME=""
    fi

    # Get session timing
    if [[ -f "$SESSION_META" ]]; then
      SESSION_START=$(jq -r '.start' "$SESSION_META" 2>/dev/null)
    else
      SESSION_START="unknown"
    fi
    SESSION_END=$(date '+%Y-%m-%d %H:%M:%S')

    echo "═══════════════════════════════════════════════════════════"
    echo "                    AGENT/MCP CALL REPORT"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "## Session Timing"
    echo "- Session Start: $SESSION_START"
    echo "- Session End: $SESSION_END"
    echo "- Session ID: ${SESSION_ID}"
    if [[ -n "$MARKER_TIME" ]]; then
      echo "- Tracking From: $MARKER_TIME (line $START_LINE)"
    fi
    echo ""
    echo "## Call Log (auto-tracked)"
    echo ""
    echo "| # | Type | Description | Start | End | Duration | Status |"
    echo "|---|------|-------------|-------|-----|----------|--------|"

    TOTAL=0
    SUCCESS=0
    FAILED=0
    LINE_NUM=0
    DISPLAY_NUM=0

    while IFS='|' read -r seq tool desc start end dur status; do
      LINE_NUM=$((LINE_NUM + 1))
      # Skip lines before start marker
      if [[ $LINE_NUM -le $START_LINE ]]; then
        continue
      fi
      DISPLAY_NUM=$((DISPLAY_NUM + 1))
      echo "| $DISPLAY_NUM | $tool | $desc | $start | $end | $dur | $status |"
      DUR_NUM=$(echo "$dur" | sed 's/s//')
      TOTAL=$((TOTAL + DUR_NUM))
      if [[ "$status" == "ok" ]]; then
        SUCCESS=$((SUCCESS + 1))
      else
        FAILED=$((FAILED + 1))
      fi
    done < "$LOG_FILE"

    echo ""
    echo "## Summary"
    echo "- Total calls: $((SUCCESS + FAILED))"
    echo "- Successful: $SUCCESS | Failed: $FAILED"
    echo "- Sum of durations: ${TOTAL}s"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    ;;

  reset)
    SESSION_ARG="$2"
    if [[ -n "$SESSION_ARG" ]]; then
      rm -f "$LOG_DIR"/session_${SESSION_ARG}.* "$LOG_DIR"/state_${SESSION_ARG}_*.json
    else
      rm -f "$LOG_DIR"/*.log "$LOG_DIR"/*.meta "$LOG_DIR"/*.json "$LOG_DIR"/*.lock
      rmdir "$LOG_DIR"/*.lock 2>/dev/null
    fi
    echo "Call log reset."
    ;;

  list)
    echo "Available sessions:"
    ls -t "$LOG_DIR"/session_*.log 2>/dev/null | while read f; do
      SID=$(basename "$f" | sed 's/session_//' | sed 's/\.log//')
      CALLS=$(wc -l < "$f" | tr -d ' ')
      echo "  - $SID ($CALLS calls)"
    done
    ;;

  *)
    echo "Usage: call-tracker.sh <pre|post|start|report|reset|list> [session_id]"
    echo ""
    echo "Actions:"
    echo "  pre    - Record call start (reads hook JSON from stdin)"
    echo "  post   - Record call end (reads hook JSON from stdin)"
    echo "  start  - Mark tracking start point (report shows only calls after this)"
    echo "  report - Generate call report (optional: session_id)"
    echo "  reset  - Clear logs (optional: session_id)"
    echo "  list   - List all sessions"
    ;;
esac
