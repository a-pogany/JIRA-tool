# JIRA Ticket Generator

> **Transform unstructured text into production-ready Jira tickets using AI-powered extraction**

Convert meeting notes, design discussions, bug reports, or any text into comprehensive, first-class Jira tickets with complete specifications, acceptance criteria, and production-ready details.

**Status**: Phase 1 ✅ **PRODUCTION READY** | Phase 2 ⏭️ Planned

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/a-pogany/JIRA-tool.git
cd JIRA-tool
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - JIRA credentials (optional for Phase 1)
```

### 3. Generate Tickets

```bash
# Validate configuration
python3 jira_gen.py validate

# Extract tickets from text
python3 jira_gen.py parse your_notes.txt --project PROJ

# Or from clipboard
python3 jira_gen.py parse --clipboard --issue-type bug --project PROJ
```

**That's it!** The tool will extract structured, high-quality Jira tickets from your text.

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

### Phase 1 (✅ Available Now)

- ✅ **AI-Powered Extraction**: Uses OpenAI/Anthropic to extract structured tickets
- ✅ **4 Issue Types**: Tasks/Epics, Bug Reports, User Stories, Epic-only planning
- ✅ **High-Quality Output**: 6-8 acceptance criteria per task (exceeds requirements!)
- ✅ **LLM Fallback**: Works without LLM using simple extraction
- ✅ **Multiple Input Sources**: Files, clipboard, stdin
- ✅ **Comprehensive Details**: Security, performance, testing, edge cases

### Phase 2 (⏭️ Coming Soon)

- ⏭️ **Review Agent**: Validates completeness and asks clarifying questions
- ⏭️ **Markdown Output**: Human-editable intermediate format
- ⏭️ **Jira Integration**: Direct upload to Jira with proper linking
- ⏭️ **Interactive Q&A**: Fill gaps through conversation

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

### Phase 2 (Planned)

```
         ↓
Agent 2: Review Agent
  • Validate completeness
  • Identify gaps
  • Ask clarifying questions
         ↓
User Interactive Q&A Session
         ↓
Markdown Generation
  • Timestamped files
  • Human-editable format
         ↓
Jira API Upload
  • Create epics and tasks
  • Link relationships
```

---

## 📂 Project Structure

```
jira-tool/
├── jira_gen.py              # ✅ Main CLI (parse, validate)
├── config.py                # ✅ Configuration management
├── models.py                # ✅ Pydantic models (Task, Epic, Bug, Story)
│
├── agents/
│   ├── extraction_agent.py  # ✅ Agent 1: LLM extraction
│   ├── prompts.py           # ✅ Prompts for all issue types
│   └── review_agent.py      # ⏭️ Agent 2 (Phase 2)
│
├── .env                     # ✅ Your configuration (gitignored)
├── .env.example             # ✅ Configuration template
├── requirements.txt         # ✅ Dependencies
│
├── test_*.txt               # ✅ Sample test inputs
├── PHASE1_STATUS.md         # ✅ Implementation status
├── TEST_REPORT.md           # ✅ Test results (16/16 passed!)
│
└── jira_client.py           # ⏭️ Jira API (Phase 2)
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

### ⏭️ Phase 2 (Planned)
- ⏭️ Review Agent for validation
- ⏭️ Interactive Q&A session
- ⏭️ Markdown generation
- ⏭️ Jira API integration
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
