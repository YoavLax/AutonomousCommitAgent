# GreenGitHub - Autonomous Commit Agent 🤖🟩

A standalone autonomous agent that **keeps your GitHub contribution graph green** by making intelligent daily commits using GitHub Copilot SDK.

## Features

- 🔄 **Daily Commits**: Automatically commits at scheduled times (default: 10:00 AM & 6:00 PM)
- 🧠 **AI-Powered Improvements**: Uses GitHub Copilot SDK to suggest meaningful changes
- 🚀 **Full Automation**: Suggests → Applies → Commits → Pushes
- 📝 **Smart Changes**: Adds documentation, improvements, examples, and helpful content
- ⚡ **Standalone**: No complex setup, runs independently

## Prerequisites

1. **Python 3.9+**
2. **GitHub Copilot SDK** (installed via pip, see below)
3. **GitHub Copilot Subscription** - Required for AI features: https://github.com/features/copilot/plans
4. **Git Repository** with PAT authentication configured

## Installation

```powershell
# Clone the repository
git clone https://github.com/YoavLax/GreenGitHub.git
cd GreenGitHub

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Configure Your Target Repository

```powershell
# Set target repository path (where agent will make commits)
$env:TARGET_REPO_PATH = "C:\path\to\your\target-repo"

# Ensure target repo has PAT authentication
cd C:\path\to\your\target-repo
git remote set-url origin https://<PAT_TOKEN>@github.com/<USER>/<REPO>.git
```

### 2. Run the Agent

**Test Mode (run once immediately):**
```powershell
python autonomous_agent.py once
```

**Production Mode (scheduled at 10:00 AM & 6:00 PM daily):**
```powershell
python autonomous_agent.py
```

Press Ctrl+C to stop the scheduler.

## Configuration

Edit `autonomous_agent.py` to customize:

```python
TARGET_REPO_PATH = os.getenv("TARGET_REPO_PATH", "")  # Your repo path
COMMIT_TIMES = ["10:00", "18:00"]  # Daily commit times (24-hour format)
AUTONOMOUS_AGENT_ENABLED = True  # Enable/disable agent
```

Or use environment variables:
```powershell
$env:TARGET_REPO_PATH = "C:\your\repo"
$env:AUTONOMOUS_AGENT_ENABLED = "true"
```

## Project Structure

```
GreenGitHub/
├── autonomous_agent.py       # 🤖 Main agent script (standalone)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## How It Works

1. **Checks Repository**: Verifies target repo is clean (no uncommitted changes)
2. **Asks Copilot**: Requests an improvement suggestion from GitHub Copilot SDK
3. **Applies Changes**: Parses the response and creates/modifies files
4. **Commits**: Stages changes and creates a meaningful commit message
5. **Pushes**: Pushes to GitHub automatically

## Example Output

```
🤖 AUTONOMOUS COMMIT AGENT - EXECUTION STARTED
📁 Repository: C:\Users\ylax\source\repos\testgreengithub\test
⏰ Time: 2026-01-27 13:30:56
✓ Repository is clean
🤖 Initializing Copilot...
✓ Copilot started
✓ Session created
💡 Requesting improvement suggestion...
Waiting for response........................
✓ Received response (214 chars)
📝 Applying changes...
✓ Created/modified: README.md
🚀 Committing changes...
✓ Changes staged
✓ Commit created: 51b8e548
✓ Pushed to remote
✅ AUTONOMOUS COMMIT COMPLETED SUCCESSFULLY
```

**Your GitHub graph stays green! 🟩**

## Notes

- Uses the official GitHub Copilot SDK: https://github.com/github/copilot-sdk
- Requires active Copilot subscription and authenticated session
- Target repository must have PAT authentication configured for push access
- Agent runs in foreground when scheduled (scheduler mode)
- Commits are real, meaningful improvements suggested by Copilot AI

## License

MIT
