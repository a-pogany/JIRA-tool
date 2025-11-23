# JIRA Ticket Generator

> **Transform unstructured text into production-ready Jira tickets using AI-powered two-agent quality assurance**

Convert meeting notes, design discussions, or any text into comprehensive, first-class Jira tickets with complete specifications, acceptance criteria, and production-ready details.

## 🎯 Overview

The JIRA Ticket Generator uses a **two-agent AI system** to ensure every generated ticket is complete, unambiguous, and ready for implementation:

1. **Agent 1 (Extraction)**: Extracts epics, tasks, and acceptance criteria from text
2. **Agent 2 (Review)**: Validates completeness, identifies gaps, and asks clarifying questions

This approach ensures **zero ambiguity** and **first-class quality** - every ticket has all necessary information for developers to implement without asking questions.

## ✨ Key Features

- **AI-Powered Parsing**: Uses OpenAI/Anthropic to extract structured tickets from free-form text
- **Two-Agent Quality Assurance**: Review agent validates completeness and spots missing requirements
- **Interactive Refinement**: Answer questions to fill gaps before ticket creation
- **Markdown Editing**: Human-editable intermediate format for full control
- **First-Class Quality**: Production-ready tickets with security, performance, testing, and deployment details
- **Single Configuration**: One `.env` file for all settings
- **LLM-Independent Fallback**: Works with simple parsing when LLM unavailable

## 📋 Quick Example

**Input text:**
```
Build user authentication system. Users should be able to
login with email and password. Add password reset via email.
```

**Generated output includes:**
- Complete epic with business value
- Multiple tasks with detailed descriptions
- 5+ acceptance criteria per task (functional, security, performance, edge cases)
- Technical specifications (database schemas, API contracts)
- Testing requirements
- Monitoring and deployment strategies

See [DESIGN.md](DESIGN.md) for complete examples.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI or Anthropic API key
- Jira account with API access

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/JIRA-tool.git
cd JIRA-tool

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with:

```bash
# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# LLM Configuration
LLM_PROVIDER=openai              # or 'anthropic'
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4-turbo

# Application Settings
DEFAULT_PROJECT_KEY=PROJ
```

## 📖 Usage

### Basic Workflow

```bash
# 1. Parse text to markdown (with two-agent quality assurance)
python jira_gen.py parse meeting_notes.txt --project PROJ

# Agent 1 extracts structure
# Agent 2 reviews and asks clarifying questions
# You answer questions to improve quality

# 2. Review generated markdown
# Edit jira_tickets_YYYYMMDD_HHMMSS.md if needed

# 3. Upload to Jira
python jira_gen.py upload jira_tickets_YYYYMMDD_HHMMSS.md
```

### Advanced Usage

```bash
# Skip review agent (faster but lower quality)
python jira_gen.py parse input.txt --skip-review

# Parse from clipboard
python jira_gen.py parse --clipboard --project PROJ

# Validate before upload
python jira_gen.py validate tickets.md

# Dry-run (validate without creating tickets)
python jira_gen.py upload tickets.md --dry-run
```

## 🏗️ Architecture

The tool uses a **two-agent architecture** for quality assurance:

```
Text Input
    ↓
Agent 1: Extraction
    ↓
Initial Structure
    ↓
Agent 2: Review & Validation
    ↓
User Q&A Session
    ↓
Refined Structure
    ↓
Markdown File
    ↓
Jira Upload
```

### Agent 1: Extraction Agent
- Identifies epics and tasks
- Extracts acceptance criteria
- Infers technical requirements
- Adds implicit requirements (error handling, testing, monitoring)

### Agent 2: Review Agent
- Validates completeness (3+ acceptance criteria per task)
- Detects ambiguities and vague language
- Identifies missing tasks (database migrations, security, testing)
- Generates specific questions for user
- Ensures production readiness

## 📂 Project Structure

```
jira-ticket-tool/
├── jira_gen.py                # Main CLI
├── config.py                  # Config (.env only)
├── models.py                  # Data models
├── agents/
│   ├── extraction_agent.py    # Agent 1: Extract structure
│   ├── review_agent.py        # Agent 2: Validate & improve
│   └── prompts.py             # LLM prompts for both agents
├── jira_client.py             # Jira API wrapper
├── markdown_utils.py          # Read/write markdown
├── .env                       # SINGLE config file
└── tests/
    ├── test_extraction_agent.py
    ├── test_review_agent.py
    └── test_integration.py
```

## 📚 Documentation

- **[DESIGN.md](DESIGN.md)**: Complete two-agent architecture specification
- **[prj-definition.md](prj-definition.md)**: Detailed project requirements and implementation plan

## 🎯 Quality Standards

Every generated ticket includes:

✅ **Business Context**: WHY this feature matters, WHO benefits
✅ **Technical Completeness**: Specific technologies, APIs, database schemas
✅ **Comprehensive Acceptance Criteria**: 5+ criteria covering functional, security, performance, edge cases
✅ **Production Readiness**: Database migrations, rollback procedures, monitoring, alerts
✅ **Security First**: Authentication, input validation, rate limiting, audit logging
✅ **Testing Requirements**: Unit, integration, E2E, load, and security tests

### Quality Metrics

**Excellent Ticket:**
- 5+ acceptance criteria
- Specific technologies mentioned
- Database schema changes specified
- API contracts defined
- Error messages specified exactly
- Performance requirements quantified (200ms, 1000 req/sec)
- Testing requirements explicit
- Rollback strategy defined

## 🔧 Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests
pytest
```

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run linters
black .
mypy .

# Type checking
mypy jira_gen.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Two-agent architecture inspired by the need for systematic quality assurance
- LLM prompt engineering for first-class ticket quality
- Focus on developer autonomy - tickets so complete developers never need to ask questions

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in DESIGN.md
- Review example outputs in the documentation

---

**Built with focus on first-class quality, zero ambiguity, and production-ready specifications** 🎯
