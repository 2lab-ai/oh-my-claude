#!/bin/bash
# Play notification sound when Claude session ends
# Uses macOS afplay for system sound

# macOS notification sound
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Use system notification sound (Glass)
    afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &
fi

exit 0
