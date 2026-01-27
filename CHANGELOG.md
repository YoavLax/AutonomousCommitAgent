# Changelog

All notable changes to GreenGitHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-27

### Added
- Initial release of GreenGitHub autonomous commit agent
- Standalone Python script for automated GitHub commits
- GitHub Copilot SDK integration for AI-powered improvements
- APScheduler for configurable daily commit times
- Git operations using GitPython
- Event-driven response collection with progress indicators
- Configuration via environment variables or direct script editing
- Support for scheduled execution (default: 10:00 AM & 6:00 PM)
- Support for one-time execution mode for testing
- Automatic commit message generation
- PAT-based authentication support
- Clean repository validation before commits

### Features
- 🔄 Automated daily commits at scheduled times
- 🧠 AI-powered improvement suggestions via Copilot
- 🚀 Full automation: Suggest → Apply → Commit → Push
- 📝 Smart changes to documentation and code
- ⚡ Standalone operation with minimal dependencies

### Technical Details
- Python 3.9+ support
- Dependencies: github-copilot-sdk, gitpython, APScheduler
- Async/await architecture
- Real-time progress feedback
- Error handling and timeout protection
