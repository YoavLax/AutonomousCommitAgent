"""Standalone autonomous GitHub commit agent - completely independent of OptiWatch."""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configuration
TARGET_REPO_PATH = "C:\\Users\\ylax\\source\\repos\\testgreengithub\\test"
COMMIT_TIMES = ["03:00","06:00","09:00", "12:00","15:00", "18:00", "21:00", "00:00"]  # Daily commit times (24-hour format)
AUTONOMOUS_AGENT_ENABLED = os.getenv("AUTONOMOUS_AGENT_ENABLED", "true").lower() == "true"


async def make_autonomous_commit(repo_path: str) -> bool:
    """Make an autonomous commit using simple direct approach."""
    from git import Repo
    from copilot import CopilotClient
    
    print("\n" + "=" * 70)
    print("🤖 AUTONOMOUS COMMIT AGENT - EXECUTION STARTED")
    print("=" * 70)
    print(f"📁 Repository: {repo_path}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize git repo
        repo = Repo(repo_path)
        
        # Check for uncommitted changes
        if repo.is_dirty() or repo.untracked_files:
            print("⚠️  Repository has uncommitted changes. Skipping.")
            return False
        
        print("✓ Repository is clean")
        
        # Analyze repository structure
        print("\n🔍 Analyzing repository...")
        repo_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            dirs[:] = [d for d in dirs if d != '.git']
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                repo_files.append(rel_path)
        
        repo_summary = f"Repository contains {len(repo_files)} files"
        if repo_files:
            file_types = {}
            for f in repo_files[:20]:  # Show first 20 files
                ext = os.path.splitext(f)[1] or 'no-ext'
                file_types[ext] = file_types.get(ext, 0) + 1
            repo_summary += f"\nFile types: {dict(file_types)}\nSample files: {', '.join(repo_files[:10])}"
        print(f"✓ Found {len(repo_files)} files")
        
        # Initialize Copilot client
        print("\n🤖 Initializing Copilot...")
        copilot = CopilotClient(options={"cli_path": "copilot.cmd"})
        await copilot.start()
        print("✓ Copilot started")
        
        # Create session
        session = await copilot.create_session({
            "model": "gpt-4.1",
            "streaming": True
        })
        print("✓ Session created")
        
        # Collect response
        response_parts = []
        complete = False
        
        def handler(event):
            nonlocal complete
            event_type = str(event.type.value if hasattr(event.type, 'value') else event.type)
            
            if event_type == "assistant.message_delta":
                if hasattr(event, 'data') and hasattr(event.data, 'delta_content'):
                    response_parts.append(event.data.delta_content)
                    print(".", end="", flush=True)
            elif event_type in ["session.idle", "assistant.message_done"]:
                complete = True
        
        session.on(handler)
        
        # Ask for improvement
        print("\n💡 Requesting improvement suggestion...")
        prompt = f"""You are an autonomous software engineer. Analyze the repository at {repo_path} and implement ONE meaningful feature or enhancement.

REPOSITORY CONTEXT:
{repo_summary}

CRITICAL RULES:
1. ANALYZE EXISTING CODE FIRST - Look at what's already there, understand the project's purpose
2. ADD REAL FUNCTIONALITY - Not documentation, not README updates
3. BE AMBITIOUS - Add features that users would actually want
4. WRITE PRODUCTION-QUALITY CODE - Include error handling, type hints, comments
5. DON'T CREATE UTIL FILES - Integrate into existing files.

SUGGESTED IMPROVEMENTS (choose the most impactful):
- Implement a NEW FEATURE that extends the project's capabilities
- Add comprehensive test suite for existing functionality
- Create API endpoints or CLI commands that users need
- Build data processing pipelines or automation scripts
- Add caching, optimization, or performance improvements
- Implement authentication, validation, or security features
- Create database models, migrations, or data access layers
- Add integrations with external services or APIs
- Build monitoring, logging, or debugging utilities
- Refactor complex code into maintainable modules

DELIVERABLE FORMAT:
FILE: <path/filename.ext>
CONTENT:
<Complete, working, production-ready code>

Think like a senior engineer: What would make this project significantly better?"""
        
        await session.send({"prompt": prompt})
        
        # Wait for response
        print("Waiting for response", end="", flush=True)
        timeout = 60
        waited = 0
        while not complete and waited < timeout:
            await asyncio.sleep(0.5)
            waited += 0.5
        
        print()
        
        response = "".join(response_parts)
        
        if not response or len(response) < 50:
            print(f"❌ No valid response received (got {len(response)} chars)")
            return False
        
        print(f"✓ Received response ({len(response)} chars)")
        print("\n📄 Response preview:")
        print(response[:300])
        print("...")
        
        # Parse and apply changes
        print("\n📝 Applying changes...")
        
        # Enhanced parsing - look for FILE: and CONTENT: (case insensitive, flexible)
        lines = response.split('\n')
        filename = None
        content_lines = []
        in_content = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Look for FILE: marker (case insensitive)
            if line_lower.startswith("file:"):
                filename = line.split(":", 1)[1].strip()
                # Remove common markdown formatting
                filename = filename.strip('`').strip()
            
            # Look for CONTENT: marker (case insensitive)
            elif line_lower.startswith("content:"):
                in_content = True
                # Check if content is on the same line
                if len(line.split(":", 1)) > 1:
                    content_on_line = line.split(":", 1)[1].strip()
                    if content_on_line:
                        content_lines.append(content_on_line)
            
            # Collect content after CONTENT: marker
            elif in_content:
                # Skip markdown code block markers
                if line.strip() in ['```python', '```javascript', '```js', '```', '```py']:
                    continue
                content_lines.append(line)
        
        # Clean up trailing empty lines
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        if not filename or not content_lines:
            print(f"❌ Failed to parse valid FILE and CONTENT from response")
            print(f"Response was: {response[:500]}")
            return False
        
        # Write file
        file_path = Path(repo_path) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        print(f"✓ Created/modified: {filename}")
        
        # Git operations
        print("\n🚀 Committing changes...")
        
        # Stage
        repo.git.add(A=True)
        print("✓ Changes staged")
        
        # Commit (skip hooks to avoid WSL/bash issues)
        commit_message = f"feat: autonomous improvement to {filename}\n\nAutomated commit by autonomous agent"
        commit = repo.git.commit('-m', commit_message, '--no-verify')
        # Get the commit hash
        commit_hash = repo.head.commit.hexsha[:8]
        print(f"✓ Commit created: {commit_hash}")
        
        # Push
        origin = repo.remote('origin')
        origin.push()
        print("✓ Pushed to remote")
        
        print("\n" + "=" * 70)
        print("✅ AUTONOMOUS COMMIT COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def scheduled_task():
    """Scheduled task wrapper."""
    if not TARGET_REPO_PATH:
        print("⚠️  TARGET_REPO_PATH not configured")
        return
    
    await make_autonomous_commit(TARGET_REPO_PATH)


def start_scheduler():
    """Start the autonomous agent scheduler."""
    if not AUTONOMOUS_AGENT_ENABLED:
        print("ℹ️  Autonomous agent is disabled")
        return
    
    if not TARGET_REPO_PATH:
        print("⚠️  TARGET_REPO_PATH not configured")
        return
    
    print("\n" + "=" * 70)
    print("🤖 AUTONOMOUS AGENT - STARTING SCHEDULER")
    print("=" * 70)
    print(f"📁 Target Repository: {TARGET_REPO_PATH}")
    print(f"⏰ Scheduled Times: {', '.join(COMMIT_TIMES)}")
    
    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create scheduler
    scheduler = AsyncIOScheduler(event_loop=loop)
    
    # Schedule tasks
    for time_str in COMMIT_TIMES:
        hour, minute = map(int, time_str.split(":"))
        trigger = CronTrigger(hour=hour, minute=minute)
        scheduler.add_job(scheduled_task, trigger=trigger, id=f"commit_{time_str}")
        print(f"✓ Scheduled commit at {time_str}")
    
    # Start scheduler
    scheduler.start()
    print("\n📅 Next executions:")
    for job in scheduler.get_jobs():
        if job.next_run_time:
            print(f"  • {job.id}: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("=" * 70)
    print("\n✓ Scheduler running. Press Ctrl+C to stop.\n")
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping scheduler...")
        scheduler.shutdown()
        print("✓ Scheduler stopped")


async def run_once():
    """Run the agent once immediately."""
    if not TARGET_REPO_PATH:
        repo_path = input("Enter target repository path: ").strip()
    else:
        repo_path = TARGET_REPO_PATH
    
    if not repo_path:
        print("❌ No repository path provided")
        return
    
    await make_autonomous_commit(repo_path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once immediately
        asyncio.run(run_once())
    else:
        # Start scheduler
        start_scheduler()
