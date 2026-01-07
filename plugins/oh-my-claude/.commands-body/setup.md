# /setup - Install Dependencies

## Task

Install and verify all required dependencies for oh-my-claude plugin.

## Steps

### 1. Install Codex (OpenAI CLI)

```bash
brew install --cask codex
```

### 2. Install Gemini CLI

```bash
brew install gemini-cli
```

### 3. Verify Installations

After installation, verify both tools are working:

**Gemini verification:**
```bash
gemini "whats your name"
```

**Codex verification:**
```bash
codex exec "whats your name"
```

## Expected Output

After running this setup, you should see:
- Gemini responds with its name/identity
- Codex responds with its name/identity (confirms authentication and model access)

## Troubleshooting

If commands fail:
- `brew update && brew upgrade` to update homebrew
- Check PATH includes `/opt/homebrew/bin`
- For codex: may need to login with `codex login`
- For gemini: may need to authenticate with Google
