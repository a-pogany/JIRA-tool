# JIRA Ticket Generator

> **Transform unstructured text into production-ready Jira tickets using AI-powered extraction**

Convert meeting notes, design discussions, bug reports, or any text into comprehensive, first-class Jira tickets with complete specifications, acceptance criteria, and production-ready details.

**Status**: Phase 1 ✅ **PRODUCTION READY** | Phase 2 Core ✅ **COMPLETE** | Phase 2 UI ✅ **COMPLETE**

---

## 🚀 Quick Start

### 1. Install & Setup

```bash
git clone https://github.com/a-pogany/JIRA-tool.git
cd JIRA-tool
./start.sh  # Automated setup: venv, dependencies, config validation
```

The start script will:
- ✅ Check Python version
- ✅ Create and activate virtual environment
- ✅ Install dependencies
- ✅ Create .env from template
- ✅ Validate configuration

### 2. Configure

Edit `.env` with your API keys:
```bash
# Required for LLM extraction (choose one)
LLM_PROVIDER=openai              # or 'anthropic'
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional - for Jira upload
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### 3. Generate Tickets

```bash
# Extract tickets with AI review
python3 jira_gen.py parse your_notes.txt --project PROJ

# Answer clarifying questions from Agent 2
# > Q1: What authentication method? [Your answer...]

# Output: jira_tickets_PROJ_task_20251123_155045.md
```

### 4. System Management

```bash
./status.sh  # Check system health (7-point check)
./stop.sh    # Cleanup and deactivation
```

**That's it!** The two-agent system will extract and validate production-ready Jira tickets.

---

## 📋 What You Get

**Input:**
```
Build user authentication system. Users should be able to
login with email and password. Add password reset via email.
Make sure to add rate limiting to prevent brute force attacks.
```

**Output:** ✨
```
Epic: User Authentication System
├─ Task 1: Implement login endpoint with JWT authentication
│  ├─ Acceptance Criteria (7+):
│  │  • Functional: POST /api/auth/login accepts email and password
│  │  • Security: Rate limiting of 5 attempts per minute per IP
│  │  • Error: Invalid credentials return 401 with message
│  │  • Performance: Login completes within 200ms
│  │  • Testing: Unit tests for token generation
│  │  • Edge: Handles SQL injection attempts safely
│  │  • Edge: Rejects missing fields
│  └─ Technical Notes: bcrypt, JWT, httpOnly cookies
└─ Task 2: Implement password reset functionality
   └─ Acceptance Criteria (6+): ...
```

---

## ✨ Key Features

### Phase 1 (✅ Complete)

- ✅ **AI-Powered Extraction**: Uses OpenAI/Anthropic to extract structured tickets
- ✅ **4 Issue Types**: Tasks/Epics, Bug Reports, User Stories, Epic-only planning
- ✅ **High-Quality Output**: 6-8 acceptance criteria per task (exceeds requirements!)
- ✅ **LLM Fallback**: Works without LLM using simple extraction
- ✅ **Multiple Input Sources**: Files, clipboard, stdin
- ✅ **Comprehensive Details**: Security, performance, testing, edge cases

### Phase 2 Core (✅ Complete)

- ✅ **Review Agent (Agent 2)**: Validates completeness and asks clarifying questions
- ✅ **Markdown Output**: Human-editable timestamped markdown files
- ✅ **Jira API Client**: Direct upload to Jira with parent-child linking
- ✅ **Interactive Q&A**: Fill gaps through conversation with Agent 2
- ✅ **Shell Scripts**: Automated setup, health check, and cleanup tools

### Phase 2 UI (✅ Complete)

- ✅ **Web Interface**: React + Flask for browser-based usage
- ✅ **File Upload & Text Input**: Upload files or paste text directly
- ✅ **Markdown Editor**: Edit generated tickets before upload
- ✅ **File Management**: Browse, view, edit, delete generated markdown files
- ✅ **Issue Type Selection**: Choose from Tasks, Bugs, Stories, Epic-only
- ✅ **Review Agent Toggle**: Optional AI review for faster generation
- ✅ **Statistics Display**: View counts of epics, tasks, bugs, stories
- ✅ **Shell Scripts**: `start-ui.sh` and `stop-ui.sh` for easy management

**Quick Start UI:**
```bash
./start-ui.sh  # Starts Flask (port 5000) + React (port 3000)
# Opens http://localhost:3000 automatically
```

See [ui/README.md](ui/README.md) for comprehensive UI documentation.

---

## 📖 User Guide

### Issue Types

The tool supports 4 different Jira issue types via `--issue-type`:

#### 1. Tasks/Epics (default)
Best for: Feature development, new functionality

```bash
python3 jira_gen.py parse feature.txt --issue-type task --project PROJ
```

**Creates:**
- Epics with business value
- Tasks with 6-8 acceptance criteria
- Technical specifications
- Security and performance requirements

**Example Input:**
```
Build a dashboard for analytics. Users need to see key metrics,
charts, and export data. Support filtering by date range.
```

#### 2. Bug Reports
Best for: Defect tracking, issue reporting

```bash
python3 jira_gen.py parse bug.txt --issue-type bug --project PROJ
```

**Creates:**
- Bug summary with clear title
- Detailed reproduction steps
- Environment information
- Severity and priority assessment

**Example Input:**
```
Login button doesn't work on Safari iOS. When users click it,
nothing happens. Steps: 1) Open Safari iOS 15+, 2) Go to login page,
3) Click button, 4) No action occurs.
```

#### 3. User Stories
Best for: Agile workflows, user-centric features

```bash
python3 jira_gen.py parse story.txt --issue-type story --project PROJ
```

**Creates:**
- "As a / I want to / So that" format
- Acceptance criteria in Given/When/Then format
- Priority and effort estimation

**Example Input:**
```
Users need to reset their password if they forget it.
They should receive an email with a reset link.
```

#### 4. Epic-Only
Best for: High-level planning without detailed tasks

```bash
python3 jira_gen.py parse epic.txt --issue-type epic-only --project PROJ
```

**Creates:**
- High-level epics with business value
- Associated tasks with requirements
- Strategic overview

---

### Configuration

Edit `.env` file with your settings:

```bash
# Required for LLM extraction (choose one)
LLM_PROVIDER=openai              # or 'anthropic'
OPENAI_API_KEY=sk-...            # Get from platform.openai.com
ANTHROPIC_API_KEY=sk-ant-...     # Get from console.anthropic.com
LLM_MODEL=gpt-4-turbo            # or 'claude-3-opus-20240229'

# Optional (for Phase 2)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Optional
DEFAULT_PROJECT_KEY=PROJ          # Default project for tickets
```

**Validate configuration:**
```bash
python3 jira_gen.py validate
```

---

### CLI Commands

#### `parse` - Extract tickets from text

```bash
python3 jira_gen.py parse [INPUT_FILE] [OPTIONS]
```

**Options:**
- `--issue-type, -t`: Type of tickets (task|bug|story|epic-only) [default: task]
- `--project, -p`: Jira project key (e.g., PROJ)
- `--clipboard`: Read from clipboard instead of file
- `--skip-review`: Skip Agent 2 review (Phase 2 feature)

**Examples:**
```bash
# From file with default settings
python3 jira_gen.py parse notes.txt --project PROJ

# Bug report from clipboard
python3 jira_gen.py parse --clipboard --issue-type bug --project PROJ

# User story with specific project
python3 jira_gen.py parse story.txt --issue-type story --project MYAPP
```

#### `validate` - Check configuration

```bash
python3 jira_gen.py validate
```

Shows current configuration and validates API keys.

#### `upload` - Upload markdown tickets to Jira (Phase 2)

```bash
python3 jira_gen.py upload [MARKDOWN_FILE] [OPTIONS]
```

**Options:**
- `--list`: List available markdown files
- `--dry-run`: Test without actually uploading

**Examples:**
```bash
# List available markdown files
python3 jira_gen.py upload --list

# Upload specific file
python3 jira_gen.py upload jira_tickets_PROJ_task_20251123_155045.md

# Test upload without creating tickets
python3 jira_gen.py upload --dry-run jira_tickets_PROJ_task_20251123_155045.md
```

---

## 🔧 Shell Scripts

Three convenience scripts for system management:

### `./start.sh` - Setup and Start

**Purpose**: Automated environment setup and validation

**What it does:**
1. ✅ Checks Python 3 installation
2. ✅ Creates virtual environment if missing
3. ✅ Activates virtual environment
4. ✅ Installs/updates dependencies from requirements.txt
5. ✅ Creates .env file from template if missing
6. ✅ Validates configuration
7. ✅ Shows usage examples

**Usage:**
```bash
./start.sh
```

**First-time setup:**
```bash
./start.sh
# Prompts you to edit .env file with API keys
# Run again after configuration:
./start.sh
```

**Output Example:**
```
╔════════════════════════════════════════════╗
║   JIRA Ticket Generator - Startup         ║
╚════════════════════════════════════════════╝

→ Checking Python version...
✓ Python 3.11.5 found
→ Activating virtual environment...
✓ Virtual environment activated
→ Checking dependencies...
✓ All dependencies already installed
→ Validating configuration...
✓ Configuration is valid

╔════════════════════════════════════════════╗
║   Ready to use! Here's how:               ║
╚════════════════════════════════════════════╝
```

---

### `./status.sh` - System Health Check

**Purpose**: Comprehensive 7-point system status check

**What it checks:**
1. ✅ Python installation and version
2. ✅ Virtual environment status (exists and activated)
3. ✅ Dependencies (click, pydantic, openai, anthropic)
4. ✅ Configuration file (.env) existence and validity
5. ✅ Configuration validation (API keys, Jira credentials)
6. ✅ Recent activity (markdown files created)
7. ✅ Disk space usage

**Usage:**
```bash
./status.sh
```

**Output Example (Healthy System):**
```
╔════════════════════════════════════════════╗
║   JIRA Ticket Generator - System Status   ║
╚════════════════════════════════════════════╝

[1/7] Python Installation
      ✓ Python 3.11.5 installed

[2/7] Virtual Environment
      ✓ Virtual environment exists
      ✓ Virtual environment active

[3/7] Dependencies
      ✓ All dependencies installed

[4/7] Configuration File
      ✓ .env file exists
      ✓ LLM Provider: openai
      ✓ OpenAI API key configured

[5/7] Configuration Validation
      ✓ Configuration valid
      ✓ Project: PROJ

[6/7] Recent Activity
      ✓ 3 markdown file(s) total
      ✓ 1 file(s) created in last 24h

[7/7] Disk Space
      ✓ Project size: 2.5M

╔════════════════════════════════════════════╗
║   ✓ System Status: HEALTHY                ║
╚════════════════════════════════════════════╝

🎉 All systems operational!

Quick Actions:
  • Generate tickets: python3 jira_gen.py parse input.txt --project PROJ
  • List files:       python3 jira_gen.py upload --list
```

**Output Example (Issues Detected):**
```
[2/7] Virtual Environment
      ✓ Virtual environment exists
      ! Virtual environment not activated
         → Run: source venv/bin/activate

[3/7] Dependencies
      ✗ Missing: click pydantic
         → Run: pip3 install -r requirements.txt

╔════════════════════════════════════════════╗
║   ! System Status: NEEDS ATTENTION         ║
╚════════════════════════════════════════════╝

⚠️  Some issues detected. See above for details.

Suggested Actions:
  • Run setup:       ./start.sh
  • Validate config: python3 jira_gen.py validate
```

---

### `./stop.sh` - Cleanup and Shutdown

**Purpose**: Deactivate environment and clean up old files

**What it does:**
1. ✅ Deactivates virtual environment
2. 🗑️ Optionally deletes old markdown files (>7 days)
3. 🗑️ Optionally cleans Python cache files (__pycache__, *.pyc)

**Usage:**
```bash
./stop.sh
```

**Interactive Cleanup:**
```
╔════════════════════════════════════════════╗
║   JIRA Ticket Generator - Cleanup         ║
╚════════════════════════════════════════════╝

→ Deactivating virtual environment...
✓ Virtual environment deactivated

→ Checking for old markdown files...
! Found 5 markdown file(s) older than 7 days

-rw-r--r--  jira_tickets_PROJ_20251110_143022.md
-rw-r--r--  jira_tickets_TEST_20251112_091544.md
...

Do you want to delete these old files? (y/N): y
✓ Old markdown files deleted

→ Checking for Python cache...
Do you want to clean Python cache files? (y/N): y
✓ Python cache cleaned

✓ Cleanup complete

Tip: Run ./start.sh to restart the system
```

---

### Input Sources

#### From File
```bash
python3 jira_gen.py parse meeting_notes.txt --project PROJ
```

#### From Clipboard
```bash
python3 jira_gen.py parse --clipboard --issue-type task --project PROJ
```

Requires: `pip install pyperclip`

#### From Stdin (coming soon)
```bash
echo "Build login system" | python3 jira_gen.py parse --project PROJ
```

---

## 🎯 Quality Standards

Every generated ticket includes:

| Aspect | Phase 1 Output | Example |
|--------|---------------|---------|
| **Acceptance Criteria** | 6-8 per task | "Functional: POST /api/auth/login returns JWT tokens" |
| **Security** | Always included | "Rate limiting of 5 attempts per minute per IP" |
| **Performance** | Quantified metrics | "Login request completes within 200ms" |
| **Error Handling** | Exact messages | "Invalid credentials return 401 with 'Invalid email or password'" |
| **Testing** | Explicit requirements | "Unit tests for token generation and validation" |
| **Edge Cases** | Multiple scenarios | "Handles SQL injection attempts safely" |
| **Technical Details** | Specific technologies | "Use bcrypt, JWT with 15min expiry, httpOnly cookies" |

**Quality Metrics (from testing):**
- ✅ Acceptance Criteria: 6-8 per task (target: ≥5)
- ✅ Specificity: High (exact APIs, error messages)
- ✅ Security: Always present
- ✅ Performance: Quantified metrics
- ✅ Test Coverage: Explicit requirements

---

## 🏗️ Architecture

### Phase 1 (Current)

```
User Input (text file, clipboard)
         ↓
Configuration Validation (.env)
         ↓
Agent 1: Extraction Agent
  • Select prompt by issue type
  • Call LLM (OpenAI/Anthropic)
  • Parse JSON response
  • Convert to Pydantic models
  • Fallback mode if LLM fails
         ↓
TicketStructure (models.py)
  • Epics (with nested Tasks)
  • Bugs (with reproduction steps)
  • Stories (agile format)
         ↓
Console Output Display
  • Formatted for readability
  • All acceptance criteria shown
```

### Phase 2 Core (✅ Complete)

```
         ↓
Agent 2: Review Agent
  • Validate completeness (LLM or rule-based)
  • Identify gaps and ambiguities
  • Generate clarifying questions
  • Production readiness check
         ↓
User Interactive Q&A Session
  • Present questions to user
  • Collect answers
  • Refine structure with feedback
         ↓
Markdown Generation
  • Timestamped files (jira_tickets_{PROJECT}_{TYPE}_{TIMESTAMP}.md)
  • Human-editable hierarchical format
  • Epics → Tasks → Acceptance Criteria structure
         ↓
Jira API Upload
  • Create epics, tasks, bugs, stories
  • Link parent-child relationships
  • Set priorities and metadata
```

---

## 📂 Project Structure

```
jira-tool/
├── jira_gen.py              # ✅ Main CLI (parse, validate, upload)
├── config.py                # ✅ Configuration management
├── models.py                # ✅ Pydantic models (Task, Epic, Bug, Story)
│
├── agents/
│   ├── extraction_agent.py  # ✅ Agent 1: LLM extraction
│   ├── review_agent.py      # ✅ Agent 2: Quality review & refinement
│   └── prompts.py           # ✅ Prompts for all agents
│
├── markdown_utils.py        # ✅ Markdown generation & parsing
├── jira_client.py           # ✅ Jira API integration
│
├── start.sh                 # ✅ Setup and startup script
├── stop.sh                  # ✅ Cleanup and shutdown script
├── status.sh                # ✅ System health check script
│
├── .env                     # ✅ Your configuration (gitignored)
├── .env.example             # ✅ Configuration template
├── requirements.txt         # ✅ Dependencies
│
├── test_*.txt               # ✅ Sample test inputs
├── jira_tickets_*.md        # ✅ Generated markdown files
│
├── PHASE1_STATUS.md         # ✅ Phase 1 implementation status
├── PHASE2_UI_DESIGN.md      # ✅ Phase 2 UI specifications
└── TEST_REPORT.md           # ✅ Test results (16/16 passed!)
```

---

## 🧪 Testing

**Phase 1 Test Results**: ✅ 16/16 tests passed (100%)

```bash
# Run validation
python3 jira_gen.py validate

# Test with sample inputs
python3 jira_gen.py parse test_input.txt --project TEST
python3 jira_gen.py parse test_bug.txt --issue-type bug --project TEST
python3 jira_gen.py parse test_story.txt --issue-type story --project TEST
```

See [TEST_REPORT.md](TEST_REPORT.md) for comprehensive test results.

---

## 📚 Documentation

- **[DESIGN.md](DESIGN.md)**: Complete architecture specification
- **[PHASE1_STATUS.md](PHASE1_STATUS.md)**: Implementation status tracking
- **[TEST_REPORT.md](TEST_REPORT.md)**: Comprehensive testing results
- **[prj-definition.md](prj-definition.md)**: Original project requirements

---

## 🔧 Development

### Running Tests

```bash
# Phase 1: Manual testing
python3 jira_gen.py parse test_input.txt --project TEST

# Phase 2: Automated test suite (coming soon)
pytest tests/
```

### Dependencies

```bash
pip install -r requirements.txt
```

**Required:**
- click>=8.1.0 (CLI framework)
- pydantic>=2.5.0 (Data models)
- python-dotenv>=1.0.0 (Configuration)
- openai>=1.3.0 (OpenAI LLM)
- anthropic>=0.7.0 (Anthropic LLM)

**Optional:**
- pyperclip>=1.8.2 (Clipboard support)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure quality
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🎯 Roadmap

### ✅ Phase 1 (Complete)
- ✅ Core configuration and data models
- ✅ Extraction Agent with LLM integration
- ✅ Support for 4 issue types
- ✅ High-quality output (6-8 acceptance criteria)
- ✅ Comprehensive testing (16/16 passed)

### ✅ Phase 2 Core (Complete)
- ✅ Review Agent (Agent 2) for quality validation
- ✅ Interactive Q&A session for gap filling
- ✅ Markdown generation with timestamped files
- ✅ Jira API integration with parent-child linking
- ✅ Shell scripts for system management
- ✅ Enhanced CLI with upload command

### ⏭️ Phase 2 UI (Planned)
- ⏭️ Web interface (React + Flask/FastAPI)
- ⏭️ Visual markdown editor
- ⏭️ Real-time Jira preview
- ⏭️ Automated test suite

---

## 💡 Tips & Best Practices

### Writing Better Input

**Good Input:**
```
Build user authentication system. Users need to login with email/password.
Add password reset via email. Security is important - prevent brute force.
Store passwords securely. Performance should be fast (< 200ms).
```

**Why it works:**
- Clear requirements
- Mentions security
- Includes performance expectations
- Specific features listed

**Output Quality:**
- Will generate 6-8 acceptance criteria
- Includes security requirements (rate limiting, bcrypt)
- Performance metrics specified
- Edge cases covered

### Issue Type Selection

| If you have... | Use | Creates |
|---------------|-----|---------|
| Feature ideas, requirements | `--issue-type task` | Epics + detailed Tasks |
| Bug description | `--issue-type bug` | Bug report with reproduction |
| User needs | `--issue-type story` | Agile user stories |
| High-level initiatives | `--issue-type epic-only` | Strategic epics |

---

## ❓ FAQ

**Q: Do I need an LLM API key?**
A: Highly recommended for quality output, but the tool has a fallback mode that works without LLM.

**Q: Which LLM provider is better?**
A: Both OpenAI and Anthropic work well. GPT-4 Turbo is currently the default.

**Q: How much does it cost?**
A: Depends on your LLM provider. Typical extraction uses ~1-2K tokens per request ($0.01-0.02 with GPT-4 Turbo).

**Q: Can I use this without Jira?**
A: Yes! Phase 1 works standalone. Phase 2 will add Jira integration.

**Q: What's the quality like?**
A: Excellent. Testing shows 6-8 acceptance criteria per task with specific technical details. See [TEST_REPORT.md](TEST_REPORT.md).

**Q: Is Phase 2 coming soon?**
A: Yes! Agent 2, markdown generation, and Jira API integration are planned.

---

## 🙏 Acknowledgments

- AI-powered extraction using OpenAI and Anthropic models
- Inspired by the need for high-quality, complete Jira tickets
- Focus on developer autonomy - tickets so complete no questions needed

---

**Built with focus on first-class quality, zero ambiguity, and production-ready specifications** 🎯
