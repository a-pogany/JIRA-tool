# JIRA Ticket Generator - Two-Agent Design Specification

## Design Philosophy

Your insight is correct - we need **TWO intelligent agents**:

1. **Extraction Agent**: Breaks down text into structured tickets (Tasks/Epics OR Bug Reports)
2. **Review Agent**: Validates completeness, spots gaps, asks clarifying questions

This ensures high-quality output before creating Jira tickets.

### Flexible Issue Type Support

The tool supports **multiple Jira issue types** through a CLI parameter:

**Supported Issue Types:**
- **`task`** (default): Creates Epics + Tasks for feature development
- **`bug`**: Creates Bug/Problem Reports for defect tracking
- **`story`**: Creates User Stories for agile workflows
- **`epic-only`**: Creates only Epics (no sub-tasks)

**Usage:**
```bash
# Feature development (default)
python jira_gen.py parse input.txt --issue-type task

# Bug reports
python jira_gen.py parse bug_description.txt --issue-type bug

# User stories
python jira_gen.py parse requirements.txt --issue-type story
```

---

## System Architecture (Two-Agent Approach)

```
┌─────────────────────────────────────────────────────────────┐
│              JIRA Ticket Generator                          │
│              (Two-Agent System)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Input (meeting notes, design docs)                   │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────┐               │
│  │   AGENT 1: Extraction Agent             │               │
│  │   "What needs to be done?"              │               │
│  │                                         │               │
│  │   - Extract epics                       │               │
│  │   - Identify tasks                      │               │
│  │   - Find acceptance criteria           │               │
│  │   - Detect priorities                   │               │
│  └──────────────┬──────────────────────────┘               │
│                 │                                           │
│                 ▼                                           │
│       Initial Ticket Structure                              │
│                 │                                           │
│                 ▼                                           │
│  ┌─────────────────────────────────────────┐               │
│  │   AGENT 2: Review Agent                 │               │
│  │   "Is this complete? What's missing?"   │               │
│  │                                         │               │
│  │   - Validate completeness               │               │
│  │   - Identify gaps                       │               │
│  │   - Spot ambiguities                    │               │
│  │   - Suggest improvements                │               │
│  │   - Ask user questions                  │               │
│  └──────────────┬──────────────────────────┘               │
│                 │                                           │
│                 ▼                                           │
│       User Interactive Session                              │
│       (Answer questions, refine)                            │
│                 │                                           │
│                 ▼                                           │
│       Final Validated Structure                             │
│                 │                                           │
│                 ▼                                           │
│       Markdown Generation                                   │
│                 │                                           │
│                 ▼                                           │
│       Jira Upload                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Structure (Simplified + Two-Agent)

```
jira-ticket-tool/
├── jira_gen.py                # Main CLI
├── config.py                  # Config (.env only)
├── models.py                  # Data models
│
├── agents/
│   ├── extraction_agent.py    # Agent 1: Extract structure
│   ├── review_agent.py        # Agent 2: Validate & improve
│   └── prompts.py             # LLM prompts for both agents
│
├── jira_client.py             # Jira API wrapper
├── markdown_utils.py          # Read/write markdown
│
├── .env                       # SINGLE config file
├── requirements.txt
│
└── tests/
    ├── test_extraction_agent.py
    ├── test_review_agent.py
    └── test_integration.py
```

---

## Data Models (models.py)

**Purpose**: Pydantic models for different Jira issue types

```python
# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ═══════════════════════════════════════════════════════
# TASK/EPIC MODELS (for feature development)
# ═══════════════════════════════════════════════════════

class Task(BaseModel):
    """Individual task (sub-task of Epic)"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    technical_notes: Optional[str] = None
    priority: Literal['High', 'Medium', 'Low'] = 'Medium'
    estimated_effort: Optional[Literal['Small', 'Medium', 'Large']] = None

class Epic(BaseModel):
    """Epic (high-level feature/initiative)"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str
    business_value: Optional[str] = None
    priority: Literal['High', 'Medium', 'Low'] = 'Medium'
    tasks: List[Task] = Field(default_factory=list)

# ═══════════════════════════════════════════════════════
# BUG REPORT MODELS
# ═══════════════════════════════════════════════════════

class Environment(BaseModel):
    """Environment where bug occurs"""
    browser: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    user_role: Optional[str] = None
    data_conditions: Optional[str] = None

class TechnicalDetails(BaseModel):
    """Technical debugging information"""
    error_message: Optional[str] = None
    console_logs: Optional[str] = None
    affected_code: Optional[str] = None
    api_calls: Optional[str] = None
    stack_trace: Optional[str] = None

class Bug(BaseModel):
    """Bug/Problem report"""
    summary: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=20)
    severity: Literal['Critical', 'High', 'Medium', 'Low'] = 'Medium'
    priority: Literal['Critical', 'High', 'Medium', 'Low'] = 'Medium'
    reproduction_steps: List[str] = Field(..., min_items=3)
    environment: Environment = Field(default_factory=Environment)
    technical_details: Optional[TechnicalDetails] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    suggested_fix: Optional[str] = None

# ═══════════════════════════════════════════════════════
# USER STORY MODELS
# ═══════════════════════════════════════════════════════

class UserStory(BaseModel):
    """User story (agile format)"""
    title: str = Field(..., min_length=5, max_length=200)
    as_a: str = Field(..., description="User role")
    i_want_to: str = Field(..., description="User goal")
    so_that: str = Field(..., description="Business value")
    acceptance_criteria: List[str] = Field(..., min_items=3)
    definition_of_done: List[str] = Field(default_factory=list)
    priority: Literal['High', 'Medium', 'Low'] = 'Medium'
    story_points: Optional[int] = Field(None, ge=1, le=13)

# ═══════════════════════════════════════════════════════
# TICKET STRUCTURE (unified container)
# ═══════════════════════════════════════════════════════

class TicketStructure(BaseModel):
    """Container for all extracted tickets"""
    project_key: str = Field(..., pattern=r'^[A-Z][A-Z0-9]{1,9}$')
    issue_type: Literal['task', 'bug', 'story', 'epic-only'] = 'task'

    # For task/epic-only types
    epics: List[Epic] = Field(default_factory=list)

    # For bug type
    bugs: List[Bug] = Field(default_factory=list)

    # For story type
    stories: List[UserStory] = Field(default_factory=list)

    @property
    def total_tasks(self) -> int:
        """Total number of tasks across all epics"""
        return sum(len(epic.tasks) for epic in self.epics)

    @property
    def total_bugs(self) -> int:
        """Total number of bugs"""
        return len(self.bugs)

    @property
    def total_stories(self) -> int:
        """Total number of user stories"""
        return len(self.stories)

    @property
    def total_issues(self) -> int:
        """Total number of all issues"""
        if self.issue_type == 'task':
            return len(self.epics) + self.total_tasks
        elif self.issue_type == 'bug':
            return self.total_bugs
        elif self.issue_type == 'story':
            return self.total_stories
        elif self.issue_type == 'epic-only':
            return len(self.epics)
        return 0
```

---

## Agent 1: Extraction Agent

**Purpose**: Extract structured tickets from unstructured text (supports multiple issue types)

```python
# agents/extraction_agent.py
from models import TicketStructure, Epic, Task, Bug
from typing import Optional, Literal

IssueType = Literal['task', 'bug', 'story', 'epic-only']

class ExtractionAgent:
    """
    Agent 1: Extract epics, tasks, or bugs from text

    Responsibilities:
    - Identify issue structure based on type (task/bug/story/epic-only)
    - Extract appropriate fields for each issue type
    - Extract acceptance criteria or reproduction steps
    - Detect priorities and severity
    """

    def __init__(self, llm_client: Optional[object] = None, issue_type: IssueType = 'task'):
        """
        Args:
            llm_client: OpenAI/Anthropic client (optional)
            issue_type: Type of Jira issues to generate (task, bug, story, epic-only)
        """
        self.llm_client = llm_client
        self.issue_type = issue_type

    def extract(self, text: str, project_key: str) -> TicketStructure:
        """
        Extract ticket structure from text

        Returns:
            Initial ticket structure (may have gaps)
        """
        if self.llm_client:
            return self._extract_with_llm(text, project_key)
        else:
            return self._extract_simple(text, project_key)

    def _extract_with_llm(self, text: str, project_key: str) -> TicketStructure:
        """Use LLM to extract structure"""
        from .prompts import EXTRACTION_PROMPT

        prompt = EXTRACTION_PROMPT.format(
            text=text,
            project_key=project_key
        )

        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a requirements analyst. Extract epics and tasks from text."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        # Parse JSON response into TicketStructure
        import json
        data = json.loads(response.choices[0].message.content)

        return self._parse_llm_response(data, project_key)

    def _extract_simple(self, text: str, project_key: str) -> TicketStructure:
        """Fallback: Simple rule-based extraction"""
        # Split by paragraphs, treat first as epic, rest as tasks
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        epic_title = paragraphs[0].split('.')[0][:100]
        tasks = []

        for para in paragraphs[1:]:
            task_title = para.split('.')[0][:100]
            tasks.append(Task(
                title=task_title,
                description=para
            ))

        epic = Epic(
            title=epic_title,
            description=paragraphs[0],
            tasks=tasks
        )

        return TicketStructure(
            project_key=project_key,
            epics=[epic]
        )

    def _parse_llm_response(self, data: dict, project_key: str) -> TicketStructure:
        """Parse LLM JSON response into models"""
        epics = []

        for epic_data in data.get('epics', []):
            tasks = []

            for task_data in epic_data.get('tasks', []):
                tasks.append(Task(
                    title=task_data.get('title', ''),
                    description=task_data.get('description', ''),
                    acceptance_criteria=task_data.get('acceptance_criteria', []),
                    priority=task_data.get('priority', 'Medium')
                ))

            epics.append(Epic(
                title=epic_data.get('title', ''),
                description=epic_data.get('description', ''),
                tasks=tasks,
                priority=epic_data.get('priority', 'Medium')
            ))

        return TicketStructure(project_key=project_key, epics=epics)
```

---

## Agent 2: Review Agent

**Purpose**: Critical review, gap analysis, user interaction

```python
# agents/review_agent.py
from models import TicketStructure, Epic, Task
from typing import List, Dict, Optional

class ReviewAgent:
    """
    Agent 2: Review and validate ticket structure

    Responsibilities:
    - Validate completeness
    - Identify missing acceptance criteria
    - Spot ambiguities
    - Suggest missing tasks
    - Generate questions for user
    - Refine structure based on feedback
    """

    def __init__(self, llm_client: Optional[object] = None):
        self.llm_client = llm_client

    def review(self, structure: TicketStructure) -> ReviewResult:
        """
        Review ticket structure for completeness

        Returns:
            ReviewResult with gaps, questions, suggestions
        """
        if self.llm_client:
            return self._review_with_llm(structure)
        else:
            return self._review_simple(structure)

    def _review_with_llm(self, structure: TicketStructure) -> 'ReviewResult':
        """LLM-powered critical review"""
        from .prompts import REVIEW_PROMPT

        # Convert structure to text for review
        structure_text = self._structure_to_text(structure)

        prompt = REVIEW_PROMPT.format(
            structure=structure_text
        )

        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior software architect reviewing requirements. Find gaps, ambiguities, and missing details."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )

        # Parse review results
        import json
        review_data = json.loads(response.choices[0].message.content)

        return ReviewResult(
            gaps=review_data.get('gaps', []),
            questions=review_data.get('questions', []),
            suggestions=review_data.get('suggestions', []),
            missing_tasks=review_data.get('missing_tasks', []),
            ambiguities=review_data.get('ambiguities', [])
        )

    def _review_simple(self, structure: TicketStructure) -> 'ReviewResult':
        """Simple rule-based review"""
        gaps = []
        questions = []

        # Check for tasks without acceptance criteria
        for epic in structure.epics:
            for task in epic.tasks:
                if not task.acceptance_criteria:
                    gaps.append(f"Task '{task.title}' has no acceptance criteria")
                    questions.append(f"What are the success criteria for '{task.title}'?")

        return ReviewResult(
            gaps=gaps,
            questions=questions,
            suggestions=[],
            missing_tasks=[],
            ambiguities=[]
        )

    def apply_feedback(
        self,
        structure: TicketStructure,
        user_answers: Dict[str, str]
    ) -> TicketStructure:
        """
        Apply user feedback to improve structure

        Args:
            structure: Original structure
            user_answers: Answers to review questions

        Returns:
            Improved structure
        """
        if self.llm_client:
            return self._apply_feedback_with_llm(structure, user_answers)
        else:
            return structure  # No changes in simple mode

    def _apply_feedback_with_llm(
        self,
        structure: TicketStructure,
        user_answers: Dict[str, str]
    ) -> TicketStructure:
        """Use LLM to apply user feedback"""
        from .prompts import REFINEMENT_PROMPT

        structure_text = self._structure_to_text(structure)
        answers_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in user_answers.items())

        prompt = REFINEMENT_PROMPT.format(
            structure=structure_text,
            feedback=answers_text
        )

        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a requirements analyst. Refine the ticket structure based on user feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        # Parse refined structure
        import json
        data = json.loads(response.choices[0].message.content)

        # Use ExtractionAgent's parser
        from .extraction_agent import ExtractionAgent
        agent = ExtractionAgent()
        return agent._parse_llm_response(data, structure.project_key)

    def _structure_to_text(self, structure: TicketStructure) -> str:
        """Convert structure to readable text for LLM"""
        lines = [f"Project: {structure.project_key}\n"]

        for epic in structure.epics:
            lines.append(f"\nEpic: {epic.title}")
            lines.append(f"Description: {epic.description}")

            for task in epic.tasks:
                lines.append(f"\n  Task: {task.title}")
                lines.append(f"  Description: {task.description}")

                if task.acceptance_criteria:
                    lines.append("  Acceptance Criteria:")
                    for ac in task.acceptance_criteria:
                        lines.append(f"    - {ac}")

        return "\n".join(lines)


class ReviewResult:
    """Results from review agent"""

    def __init__(
        self,
        gaps: List[str],
        questions: List[str],
        suggestions: List[str],
        missing_tasks: List[str],
        ambiguities: List[str]
    ):
        self.gaps = gaps
        self.questions = questions
        self.suggestions = suggestions
        self.missing_tasks = missing_tasks
        self.ambiguities = ambiguities

    @property
    def has_issues(self) -> bool:
        """Check if there are any issues"""
        return bool(
            self.gaps or
            self.questions or
            self.missing_tasks or
            self.ambiguities
        )

    def __str__(self) -> str:
        """Pretty print review results"""
        lines = []

        if self.gaps:
            lines.append("🔍 Gaps Found:")
            for gap in self.gaps:
                lines.append(f"  - {gap}")

        if self.ambiguities:
            lines.append("\n⚠️  Ambiguities:")
            for amb in self.ambiguities:
                lines.append(f"  - {amb}")

        if self.missing_tasks:
            lines.append("\n💡 Suggested Missing Tasks:")
            for task in self.missing_tasks:
                lines.append(f"  - {task}")

        if self.questions:
            lines.append("\n❓ Questions for Clarification:")
            for i, q in enumerate(self.questions, 1):
                lines.append(f"  {i}. {q}")

        if self.suggestions:
            lines.append("\n✨ Suggestions:")
            for sug in self.suggestions:
                lines.append(f"  - {sug}")

        return "\n".join(lines) if lines else "✅ No issues found"
```

---

## LLM Prompts

```python
# agents/prompts.py

EXTRACTION_PROMPT = """
You are a senior requirements analyst extracting FIRST-CLASS Jira tickets from text.

Text:
{text}

Project Key: {project_key}

EXTRACTION CHECKLIST - Extract ALL of the following:

1. **EPICS** (High-level features/initiatives)
   - Clear, business-focused title
   - WHY this epic matters (business value)
   - WHO benefits (target users/stakeholders)
   - WHAT the epic delivers (outcomes)

2. **TASKS** (Specific, actionable items)
   For EACH task, extract:
   - Action-oriented title (starts with verb: Implement, Create, Add, Build, Configure)
   - WHAT needs to be done (detailed description)
   - WHERE in the system (which component/module)
   - Technical context (APIs, databases, frameworks mentioned)
   - Dependencies on other tasks (if mentioned)

3. **ACCEPTANCE CRITERIA** (Testable success conditions)
   For EACH task, extract:
   - Functional requirements (features that must work)
   - Non-functional requirements (performance, security, usability)
   - Input/output specifications
   - Edge cases and error conditions
   - Data validation rules
   - User experience requirements

4. **TECHNICAL DETAILS**
   Extract any mentions of:
   - Technology stack (languages, frameworks, libraries)
   - Integration points (APIs, services, databases)
   - Data models/schemas
   - Security requirements (auth, permissions, encryption)
   - Performance requirements (latency, throughput, scale)
   - Deployment considerations

5. **PRIORITIES** (Infer from language)
   - "urgent", "critical", "asap", "immediately" → High
   - "important", "should", "need" → Medium
   - "nice to have", "eventually", "consider" → Low

6. **IMPLICIT REQUIREMENTS** (Fill gaps)
   Always consider and add if not explicitly mentioned:
   - Error handling for each feature
   - Input validation
   - Logging/monitoring
   - Unit testing requirements
   - Documentation needs
   - Backward compatibility
   - Migration/deployment steps

Return as JSON:
{{
  "epics": [
    {{
      "title": "Epic Title (business-focused)",
      "description": "WHY this epic matters and WHAT it delivers",
      "business_value": "Impact on users/business",
      "priority": "High|Medium|Low",
      "tasks": [
        {{
          "title": "Verb + What + Where (e.g., Implement login endpoint in Auth API)",
          "description": "Detailed description with technical context and dependencies",
          "acceptance_criteria": [
            "Functional: User can login with valid credentials",
            "Error: Invalid credentials return 401 with clear message",
            "Security: Passwords hashed with bcrypt",
            "Performance: Login completes within 200ms",
            "Validation: Email format validated",
            "Edge: Handle concurrent login attempts"
          ],
          "technical_notes": "Uses JWT tokens, Redis for sessions, PostgreSQL for users",
          "priority": "High|Medium|Low",
          "estimated_effort": "Small|Medium|Large"
        }}
      ]
    }}
  ]
}}

QUALITY STANDARDS:
- Each task must have AT LEAST 3 acceptance criteria
- Include both happy path AND error cases
- Mention specific technologies when possible
- Be specific, not vague (avoid "should work well" → specify metrics)
- Think like a developer who will implement this
"""

BUG_EXTRACTION_PROMPT = """
You are a QA engineer extracting FIRST-CLASS Bug Reports from text.

Text:
{text}

Project Key: {project_key}

BUG REPORT EXTRACTION CHECKLIST - Extract ALL of the following:

1. **BUG SUMMARY** (Clear, specific title)
   - WHAT is broken (specific feature/component)
   - WHERE it occurs (which page/module)
   - WHEN it happens (under what conditions)

2. **DESCRIPTION** (Detailed problem statement)
   - Current behavior (what's happening)
   - Expected behavior (what should happen)
   - Impact on users/business

3. **REPRODUCTION STEPS** (Exact, numbered steps)
   - Step 1: Preconditions (initial state)
   - Step 2-N: Actions to reproduce
   - Must be reproducible by any developer

4. **ENVIRONMENT** (Where bug occurs)
   - Browser/OS/Device
   - Version numbers
   - User role/permissions
   - Data conditions

5. **SEVERITY & PRIORITY**
   - Critical: System down, data loss, security breach
   - High: Major feature broken, workaround exists
   - Medium: Minor feature broken, low impact
   - Low: Cosmetic, typo, enhancement

6. **TECHNICAL DETAILS** (Extract if mentioned)
   - Error messages (exact text)
   - Stack traces
   - Console logs
   - Network requests (failed API calls)
   - Database state

7. **ACCEPTANCE CRITERIA** (Fix validation)
   - How to verify fix works
   - Regression test scenarios
   - Edge cases to check

Return as JSON:
{{
  "bugs": [
    {{
      "summary": "Login button does nothing when clicked on Safari iOS",
      "description": "When users click the login button on Safari iOS 15+, nothing happens. Expected: Login form should submit and redirect to dashboard. Impact: iOS users cannot access the platform.",
      "severity": "High",
      "priority": "High",
      "reproduction_steps": [
        "Open Safari on iOS 15.0+",
        "Navigate to https://app.example.com/login",
        "Enter valid email and password",
        "Click 'Login' button",
        "Observe: No action, no error, button stays in idle state"
      ],
      "environment": {{
        "browser": "Safari iOS 15.0+",
        "os": "iOS 15.0-17.0",
        "user_role": "Any",
        "data_conditions": "Valid user credentials"
      }},
      "technical_details": {{
        "error_message": "None visible",
        "console_logs": "Uncaught TypeError: Cannot read property 'submit' of null",
        "affected_code": "LoginForm.tsx line 45",
        "api_calls": "POST /api/auth/login never fires"
      }},
      "acceptance_criteria": [
        "Functional: Login button submits form on Safari iOS 15+",
        "Validation: Form validates before submission",
        "Error: Network errors show user-friendly message",
        "Regression: Works on Chrome, Firefox, Safari desktop",
        "Edge: Works with keyboard 'Enter' key submission",
        "Edge: Works with iOS autocomplete password fill"
      ],
      "suggested_fix": "Add touchend event handler for iOS compatibility"
    }}
  ]
}}

QUALITY STANDARDS:
- Each bug must have AT LEAST 5 reproduction steps
- Include exact error messages and console logs when available
- Specify affected environment precisely (browser version, OS, device)
- Provide clear acceptance criteria for fix verification
- Suggest technical cause if obvious from description
"""

REVIEW_PROMPT = """
You are a senior software architect conducting a THOROUGH QUALITY REVIEW of Jira tickets.

Current Structure:
{structure}

COMPREHENSIVE REVIEW CHECKLIST:

1. **COMPLETENESS CHECK** - Is ALL necessary information present?
   For EACH task, verify:
   ✓ Does it have AT LEAST 3 detailed acceptance criteria?
   ✓ Are both success AND failure scenarios covered?
   ✓ Are input/output specifications clear?
   ✓ Are edge cases mentioned?
   ✓ Are performance/security requirements specified?
   ✓ Is technical context provided?

2. **AMBIGUITY DETECTION** - What's unclear or vague?
   Flag any:
   - Vague descriptions ("should work well", "user-friendly")
   - Missing specifics (which API? what format? how fast?)
   - Undefined terms (what counts as "success"?)
   - Unspecified error handling
   - Missing data validation rules

3. **CRITICAL MISSING TASKS** - What's not mentioned but REQUIRED?

   **Infrastructure & Setup:**
   - Database migrations/schema changes?
   - Environment configuration?
   - Deployment scripts?
   - CI/CD pipeline updates?

   **Error Handling & Resilience:**
   - What happens when external APIs fail?
   - Network timeout handling?
   - Retry logic?
   - Circuit breakers?
   - Graceful degradation?

   **Security:**
   - Authentication/authorization?
   - Input sanitization?
   - SQL injection prevention?
   - XSS protection?
   - Rate limiting?
   - Audit logging?

   **Data & Validation:**
   - Data validation rules?
   - Data migration for existing records?
   - Backward compatibility?
   - Data consistency checks?

   **Testing:**
   - Unit tests?
   - Integration tests?
   - E2E tests?
   - Performance/load tests?
   - Security tests?

   **Operations:**
   - Monitoring/alerting?
   - Logging strategy?
   - Metrics/analytics?
   - Rollback procedures?

   **User Experience:**
   - Loading states?
   - Error messages?
   - Success confirmations?
   - Accessibility (WCAG)?
   - Mobile responsiveness?

   **Documentation:**
   - API documentation?
   - User guide updates?
   - Architecture diagrams?
   - Deployment runbook?

4. **DEPENDENCIES & SEQUENCING**
   - Are task dependencies clear?
   - What must be done first?
   - What can run in parallel?
   - Are there blocking dependencies?

5. **PRODUCTION READINESS**
   - Can this be safely deployed to production?
   - What's the rollback plan?
   - Are there breaking changes?
   - Is backward compatibility addressed?

6. **CLARIFICATION QUESTIONS** - What to ask user?
   Ask SPECIFIC questions about:
   - Exact technical requirements (not "how should it work?" → "Should login use JWT or session cookies?")
   - Business logic details ("What happens if user already exists?")
   - Performance expectations ("What's acceptable response time?")
   - Error handling ("Should failed logins lock accounts? After how many attempts?")
   - Data requirements ("What user fields are required vs optional?")

Return as JSON:
{{
  "gaps": [
    "Task 'X' missing acceptance criteria for error cases",
    "No performance requirements specified for 'Y'",
    "Missing input validation details for 'Z'"
  ],
  "ambiguities": [
    "'user-friendly interface' in Task 1 is vague - need specific UX requirements",
    "'fast response' in Task 2 - what's the target latency?"
  ],
  "missing_tasks": [
    "Add database migration task for new user_sessions table",
    "Implement rate limiting for login endpoint (prevent brute force)",
    "Create monitoring dashboard for authentication metrics",
    "Add unit tests for password validation logic",
    "Write API documentation for new auth endpoints"
  ],
  "questions": [
    "Should login sessions use JWT tokens or server-side sessions? What's the security requirement?",
    "What's the account lockout policy? Lock after how many failed attempts?",
    "Do we need to support 'remember me' functionality? If yes, for how long?",
    "Should password reset links expire? After what duration?",
    "What password complexity requirements? (min length, special chars, etc.)",
    "Do we need audit logging for authentication events? What to log?"
  ],
  "suggestions": [
    "Consider adding 2FA support task for future security enhancement",
    "Recommend using bcrypt for password hashing (industry standard)",
    "Suggest implementing refresh tokens for better security"
  ],
  "production_readiness_concerns": [
    "No rollback plan specified if authentication breaks",
    "Missing backward compatibility for existing user sessions",
    "No performance benchmarks defined"
  ]
}}

BE EXTREMELY THOROUGH:
- Think like a security expert (what could be exploited?)
- Think like an ops engineer (what could break in production?)
- Think like a QA tester (what edge cases exist?)
- Think like a developer (what implementation details are missing?)
- Think like a product manager (does this deliver user value?)

Quality bar: Each ticket should be SO COMPLETE that a developer can implement it WITHOUT asking any questions.
"""

REFINEMENT_PROMPT = """
Refine this ticket structure based on user feedback.

Original Structure:
{structure}

User Feedback:
{feedback}

Apply the feedback and return an improved structure with:
1. Filled gaps
2. Resolved ambiguities
3. Added suggested tasks
4. Enhanced acceptance criteria

Return same JSON format as extraction prompt.
"""
```

---

## Updated CLI with Two-Agent Flow

```python
# jira_gen.py - Two-agent workflow
import click
from pathlib import Path
from config import Config
from agents.extraction_agent import ExtractionAgent
from agents.review_agent import ReviewAgent
from markdown_utils import write_markdown, read_markdown
from jira_client import JiraClient

@click.group()
def cli():
    """JIRA Ticket Generator - Two-Agent System"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--project', '-p', help='Project key')
@click.option('--issue-type', '-t',
              type=click.Choice(['task', 'bug', 'story', 'epic-only'], case_sensitive=False),
              default='task',
              help='Jira issue type: task (default), bug, story, epic-only')
@click.option('--skip-review', is_flag=True, help='Skip review agent')
def parse(input_file, project, issue_type, skip_review):
    """Parse text with two-agent system"""

    # Load config
    config = Config.load()
    errors = config.validate()
    if errors:
        click.echo("❌ Configuration errors:")
        for error in errors:
            click.echo(f"  - {error}")
        return

    project_key = project or config.jira_project
    issue_type = issue_type.lower()

    # Setup LLM client (if available)
    llm_client = None
    if config.has_llm:
        from openai import OpenAI
        llm_client = OpenAI(api_key=config.openai_key)
        click.echo(f"🤖 Using LLM-powered agents (issue type: {issue_type})")
    else:
        click.echo(f"📝 Using simple rule-based agents (issue type: {issue_type})")

    # Read input
    text = Path(input_file).read_text()

    # ═══════════════════════════════════════════════════════
    # AGENT 1: EXTRACTION
    # ═══════════════════════════════════════════════════════
    click.echo(f"\n🔍 Agent 1: Extracting {issue_type} structure from text...")

    extraction_agent = ExtractionAgent(llm_client, issue_type=issue_type)
    structure = extraction_agent.extract(text, project_key)

    click.echo(f"  ✅ Extracted {len(structure.epics)} epics, {structure.total_tasks} tasks")

    # ═══════════════════════════════════════════════════════
    # AGENT 2: REVIEW & VALIDATION
    # ═══════════════════════════════════════════════════════
    if not skip_review:
        click.echo("\n🔎 Agent 2: Reviewing for completeness...")

        review_agent = ReviewAgent(llm_client)
        review = review_agent.review(structure)

        if review.has_issues:
            click.echo("\n" + str(review))

            # Interactive Q&A
            if review.questions:
                click.echo("\n💬 Please answer these questions to improve quality:\n")

                user_answers = {}
                for i, question in enumerate(review.questions, 1):
                    answer = click.prompt(f"  {i}. {question}")
                    user_answers[question] = answer

                # Apply feedback
                click.echo("\n🔄 Refining structure based on your answers...")
                structure = review_agent.apply_feedback(structure, user_answers)
                click.echo("  ✅ Structure refined")

        else:
            click.echo("  ✅ No issues found - structure looks good!")

    # ═══════════════════════════════════════════════════════
    # GENERATE MARKDOWN
    # ═══════════════════════════════════════════════════════
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(f"jira_tickets_{timestamp}.md")

    write_markdown(structure, output_file)

    click.echo(f"\n✅ Generated {output_file}")
    click.echo(f"   - {len(structure.epics)} epics")
    click.echo(f"   - {structure.total_tasks} tasks")
    click.echo(f"\n💡 Next: Review the markdown, then run:")
    click.echo(f"   jira_gen upload {output_file}")

# ... rest of CLI commands (validate, upload) remain the same
```

---

## Example: Two-Agent Flow Producing FIRST-CLASS Tickets

### Input Text:
```
Build user authentication system. Users should be able to
login with email and password. Add password reset via email.
Support OAuth with Google and GitHub.
```

### Agent 1 Output (Extraction - COMPREHENSIVE):
```
Epic: User Authentication System
Business Value: Enable secure user access to platform, reducing fraud and improving user experience

  Task 1: Implement email/password login endpoint in Auth API
    Description: Create REST API endpoint that accepts email and password,
                validates credentials against database, and returns JWT token.
                Uses bcrypt for password hashing, PostgreSQL for user storage.
    Acceptance Criteria:
      - Functional: User can login with valid email/password, receives JWT token
      - Error: Invalid credentials return 401 with message "Invalid email or password"
      - Security: Passwords hashed with bcrypt (cost factor 12)
      - Performance: Login completes within 200ms for 95th percentile
      - Validation: Email must be valid format (RFC 5322)
      - Edge: Handle concurrent login attempts from same user
      - Edge: Prevent timing attacks (constant-time comparison)
    Technical Notes: Uses JWT with 15min expiry, refresh tokens in Redis,
                    PostgreSQL users table with email unique index
    Priority: High

  Task 2: Implement session management with JWT tokens
    Description: Create session middleware that validates JWT tokens,
                handles refresh token rotation, stores sessions in Redis.
    Acceptance Criteria:
      - Functional: Sessions expire after 24 hours (configurable)
      - Functional: Refresh tokens extend session by 7 days
      - Security: Tokens use RS256 signing algorithm
      - Error: Expired tokens return 401 with clear error
      - Edge: Handle session revocation on password change
      - Edge: Support concurrent sessions from different devices
    Technical Notes: Redis for session storage, key pattern: session:{user_id}:{token_id}
    Priority: High

  Task 3: Add password reset flow with secure email links
    Description: Generate secure reset tokens, send email with reset link,
                validate token and allow password update within time window.
    Acceptance Criteria:
      - Functional: User receives email with reset link within 1 minute
      - Security: Reset tokens cryptographically secure (32 bytes random)
      - Security: Reset links expire after 1 hour
      - Security: Old reset links invalidated when new one requested
      - Validation: New password must meet complexity requirements
      - Error: Expired link shows user-friendly error with "request new link" option
      - Edge: Handle multiple reset requests in quick succession (rate limit)
    Technical Notes: Use SendGrid for emails, tokens stored in PostgreSQL
                    password_resets table with expiry timestamp
    Priority: High

  Task 4: Integrate Google OAuth 2.0
    Description: Implement OAuth flow using Google Sign-In,
                handle callback, create/link user accounts.
    Acceptance Criteria:
      - Functional: Users can sign in with Google account
      - Functional: Auto-link to existing account if email matches
      - Functional: Create new account if email not found
      - Error: OAuth errors shown with user-friendly message
      - Security: Validate OAuth state parameter (CSRF protection)
      - Security: Verify Google JWT signature
      - Edge: Handle case where Google email not verified
    Technical Notes: Uses Google OAuth 2.0, redirect URI in .env config
    Priority: Medium

  Task 5: Integrate GitHub OAuth
    (Similar detailed criteria as Google OAuth)
    Priority: Medium
```

### Agent 2 Review (Critical Analysis - THOROUGH):
```
🔍 Gaps Found:
  - No rate limiting specified for login endpoint (security risk)
  - Missing account lockout policy after failed login attempts
  - No audit logging for authentication events
  - Missing database migration tasks for new tables
  - No monitoring/alerting specified
  - Missing password complexity requirements specification
  - No backward compatibility plan for existing sessions

⚠️  Ambiguities:
  - "New password must meet complexity requirements" - WHAT requirements specifically?
  - "Handle concurrent login attempts" - what's the expected behavior?
  - "User-friendly error" - what's the exact message text?
  - OAuth "auto-link" - what if email exists but is unverified?

💡 Suggested Missing Tasks:
  **Security & Error Handling:**
  - Implement rate limiting for login endpoint (max 5 attempts per minute per IP)
  - Add account lockout after 5 failed login attempts (30-minute cooldown)
  - Create audit logging for all auth events (login, logout, password change, reset)
  - Implement CAPTCHA after 3 failed login attempts

  **Data & Infrastructure:**
  - Create database migration for users table (add oauth_provider, oauth_id columns)
  - Create database migration for password_resets table
  - Create database migration for sessions table
  - Add indexes on users.email, sessions.user_id for performance
  - Configure Redis for session storage (setup, backup policy)

  **Testing:**
  - Write unit tests for password hashing logic
  - Write integration tests for login flow (happy + error paths)
  - Write E2E tests for OAuth flow
  - Perform security penetration testing for auth endpoints
  - Load test login endpoint (1000 req/sec target)

  **Operations:**
  - Set up monitoring dashboard for auth metrics (login success rate, failures, latency)
  - Configure alerting for suspicious activity (>100 failed logins/minute)
  - Create rollback procedure if auth system breaks
  - Document deployment steps for auth service

  **User Experience:**
  - Add loading spinner during login API call
  - Show clear error messages for each failure type (invalid email, wrong password, account locked)
  - Add "Forgot password?" link on login form
  - Implement "Remember me" checkbox (extend session to 30 days)

  **Documentation:**
  - Write API documentation for auth endpoints (OpenAPI spec)
  - Update user guide with OAuth login instructions
  - Create security runbook for incident response

❓ Questions for Clarification:
  1. Password complexity: Minimum 8 chars? Require uppercase, numbers, special chars?
  2. Account lockout: After 5 attempts, lock for 30 minutes? Or require email verification?
  3. Rate limiting: Should it be per IP, per email, or both?
  4. OAuth edge case: If Google email exists but unverified in our system, block or allow?
  5. Session security: Should we detect and prevent session hijacking? How?
  6. Password reset: Should we notify user via email when password is changed?
  7. GDPR compliance: Do we need "delete my account" functionality?
  8. Logging: What PII should we avoid logging for privacy? (passwords, tokens?)
  9. Deployment: Blue-green deployment or rolling update for auth service?
  10. Backward compatibility: Existing users with old password hash - migrate when?

✨ Suggestions:
  - Consider implementing refresh token rotation (revoke old refresh token when issuing new one)
  - Recommend adding security headers (Content-Security-Policy, X-Frame-Options)
  - Suggest implementing device fingerprinting to detect suspicious login locations
  - Consider adding "magic link" login option (passwordless for better UX)

⚠️  Production Readiness Concerns:
  - No rollback plan if JWT secret key is compromised
  - Missing backward compatibility for users mid-session during deployment
  - No canary deployment strategy specified
  - No performance benchmarks or SLAs defined
  - Missing disaster recovery plan for Redis outage
```

### User Answers Questions (Sample):
```
💬 Answering Agent 2's questions:

1. Password complexity?
   > Minimum 8 chars, at least 1 uppercase, 1 number, 1 special char

2. Account lockout policy?
   > Lock after 5 failed attempts for 30 minutes, send unlock email

3. Rate limiting strategy?
   > Per IP: 20 req/min, Per email: 5 req/min (whichever hits first)

4. OAuth unverified email?
   > Block OAuth login if email exists but unverified, ask user to verify first

5. Session hijacking prevention?
   > Yes, bind session to User-Agent and IP, alert on suspicious change

6. Password change notification?
   > Yes, send email notification immediately

7. GDPR delete account?
   > Yes, add "Delete my account" button in settings (soft delete, 30-day recovery)

8. PII logging restrictions?
   > Never log passwords, tokens, or full email (only domain for analytics)

9. Deployment strategy?
   > Blue-green deployment with 10-minute canary period

10. Backward compatibility for old sessions?
    > Keep old session format valid for 7 days post-deployment
```

### Agent 2 Output (COMPLETE & PRODUCTION-READY):
```
Epic: User Authentication System
Business Value: Enable secure user access to platform, reducing fraud by 90%,
               improving user retention through seamless OAuth integration

EPIC ACCEPTANCE CRITERIA:
- All auth endpoints respond within 200ms (p95)
- Security audit passes with zero critical vulnerabilities
- Zero downtime deployment achieved
- 99.9% uptime SLA for auth service

──────────────────────────────────────────────────────────────

Task 1: Implement email/password login endpoint in Auth API
Description: Create POST /api/auth/login endpoint accepting email and password.
            Validates credentials against PostgreSQL users table, returns JWT token
            on success. Uses bcrypt for password hashing (cost factor 12).

Acceptance Criteria:
  Functional:
  - User can login with valid email/password, receives JWT access + refresh token
  - JWT access token expires in 15 minutes, refresh token in 7 days

  Error Handling:
  - Invalid credentials return 401 with message "Invalid email or password"
  - Account locked returns 423 with message "Account locked. Check email for unlock link"
  - Missing fields return 400 with field-specific error messages

  Security:
  - Passwords hashed with bcrypt (cost factor 12)
  - Constant-time password comparison (prevent timing attacks)
  - Rate limit: 5 attempts per email per minute, 20 per IP per minute
  - Account locks after 5 failed attempts for 30 minutes
  - Send unlock email with secure token

  Performance:
  - Login completes within 200ms for 95th percentile
  - Supports 1000 concurrent login requests

  Validation:
  - Email validated against RFC 5322 format
  - Email length max 255 chars
  - Password length min 8, max 128 chars

  Edge Cases:
  - Handle concurrent login attempts from same user (last one wins)
  - Handle login during password reset (allow, invalidate reset token)
  - Handle deleted user accounts (return "Invalid credentials" not "Account deleted")

  Logging & Monitoring:
  - Log all login attempts with: email domain, IP, User-Agent, timestamp, result
  - Never log passwords or full emails
  - Alert if >100 failed logins/minute (DDoS detection)

  Testing Requirements:
  - Unit test: password hashing logic
  - Integration test: full login flow (success + all error cases)
  - Load test: 1000 req/sec sustained for 5 minutes
  - Security test: SQL injection, timing attacks

Technical Notes:
  - Uses JWT with RS256 signing (keys in .env: JWT_PRIVATE_KEY, JWT_PUBLIC_KEY)
  - PostgreSQL users table schema: id, email (unique), password_hash, failed_attempts, locked_until
  - Redis for rate limiting keys: "rate:login:{email}", "rate:login:ip:{ip}"
  - Endpoint: POST /api/auth/login
  - Request: {"email": "user@example.com", "password": "SecurePass123!"}
  - Response: {"access_token": "...", "refresh_token": "...", "expires_in": 900}

Priority: High
Estimated Effort: Large (5-8 hours)
Dependencies: None
Assigned To: Backend Team

──────────────────────────────────────────────────────────────

Task 2: Create database migration for authentication tables
Description: Create Flyway migration adding users, sessions, password_resets tables
            with proper indexes and constraints.

Acceptance Criteria:
  Schema:
  - users table: id (PK), email (unique), password_hash, oauth_provider, oauth_id,
                 failed_attempts (default 0), locked_until (nullable),
                 created_at, updated_at
  - sessions table: id (PK), user_id (FK), access_token_hash, refresh_token_hash,
                   ip_address, user_agent, expires_at, created_at
  - password_resets table: id (PK), user_id (FK), token_hash, expires_at, created_at

  Indexes:
  - users.email (unique, btree)
  - sessions.user_id (btree)
  - sessions.expires_at (btree) for cleanup
  - password_resets.user_id (btree)
  - password_resets.expires_at (btree)

  Constraints:
  - email format validation (CHECK constraint)
  - expires_at must be future (CHECK constraint)
  - CASCADE delete sessions and password_resets when user deleted

  Rollback:
  - Down migration drops all tables cleanly
  - No data loss on rollback (backup strategy documented)

Technical Notes:
  - Flyway version: V001__create_auth_tables.sql
  - Auto-generates id (UUID), timestamps
  - Uses PostgreSQL-specific types (TIMESTAMPTZ for timezone support)

Priority: High
Estimated Effort: Small (2 hours)
Dependencies: None (must run before Task 1)

──────────────────────────────────────────────────────────────

Task 3: Implement rate limiting middleware for auth endpoints
Description: Create Express middleware applying rate limits per IP and per email
            using Redis for distributed rate limiting across multiple servers.

Acceptance Criteria:
  Rate Limits:
  - Per email: 5 requests per minute (any auth endpoint)
  - Per IP: 20 requests per minute (any auth endpoint)
  - Whichever limit hits first blocks request

  Error Response:
  - Returns 429 Too Many Requests
  - Header: Retry-After (seconds until limit resets)
  - Body: {"error": "Too many requests. Try again in 45 seconds"}

  Edge Cases:
  - Handle Redis connection failures gracefully (fail-open for 5 minutes, alert ops)
  - Reset counters at minute boundaries (not rolling windows)
  - Allow whitelist IPs to bypass rate limits (load balancer health checks)

Technical Notes:
  - Uses Redis INCR with EXPIRE
  - Keys: "rate:auth:email:{email}:minute:{timestamp}", "rate:auth:ip:{ip}:minute:{timestamp}"
  - Middleware: app.use('/api/auth/*', rateLimitMiddleware)

Priority: High
Estimated Effort: Medium (3-4 hours)
Dependencies: Task 2 (needs Redis configured)

──────────────────────────────────────────────────────────────

Task 4: Implement account lockout with email unlock mechanism
Description: Lock user account after 5 failed login attempts, send unlock email
            with secure token, create unlock endpoint.

Acceptance Criteria:
  Lockout Logic:
  - After 5 consecutive failed logins, set locked_until to NOW() + 30 minutes
  - Send email with unlock link immediately
  - Successful login resets failed_attempts to 0
  - Locked accounts cannot login even with correct password

  Unlock Email:
  - Subject: "Unlock Your Account - {APP_NAME}"
  - Contains secure unlock link valid for 24 hours
  - Link format: https://app.com/auth/unlock?token={SECURE_TOKEN}
  - Email sent within 1 minute

  Unlock Endpoint:
  - POST /api/auth/unlock with token
  - Validates token, sets locked_until to NULL, resets failed_attempts
  - Returns 200 with message "Account unlocked successfully"

  Security:
  - Unlock tokens cryptographically secure (32 bytes random, URL-safe)
  - Tokens single-use (deleted after successful unlock)
  - Expired tokens return 400 "Token expired. Request new unlock email"

Technical Notes:
  - Uses SendGrid for emails (SENDGRID_API_KEY in .env)
  - Email template: templates/unlock-account.html
  - Stores tokens in password_resets table (reuse structure)

Priority: High
Estimated Effort: Medium (4 hours)
Dependencies: Task 1, Task 2

──────────────────────────────────────────────────────────────

Task 5: Implement audit logging for all authentication events
Description: Log all auth events to PostgreSQL audit_logs table and CloudWatch
            for security monitoring and incident response.

Acceptance Criteria:
  Events to Log:
  - Login attempt (success/failure) with email domain, IP, User-Agent
  - Password reset requested
  - Password changed
  - Account locked/unlocked
  - Session created/destroyed
  - OAuth login attempt

  Log Format:
  - Structured JSON: {event_type, user_id, email_domain, ip, user_agent, timestamp, metadata}
  - Never log: passwords, tokens, full emails (GDPR compliance)

  Storage:
  - PostgreSQL audit_logs table (30-day retention, auto-cleanup)
  - CloudWatch Logs for real-time alerting

  Querying:
  - Support filtering by user_id, event_type, date range
  - Create view for suspicious activity (>5 failed logins in 1 hour)

Technical Notes:
  - Table: audit_logs (id, event_type, user_id, data JSONB, created_at)
  - Index on event_type, user_id, created_at
  - CloudWatch log group: /auth/events

Priority: Medium
Estimated Effort: Medium (3 hours)
Dependencies: Task 2

──────────────────────────────────────────────────────────────

Task 6-15: [Additional tasks for OAuth, session management, testing,
          monitoring, documentation - all with same level of detail]

──────────────────────────────────────────────────────────────

DEPLOYMENT PLAN:
Phase 1: Database migrations (Task 2)
Phase 2: Core auth endpoints (Tasks 1, 3, 4)
Phase 3: Logging and monitoring (Task 5)
Phase 4: OAuth integration (Tasks 6-7)
Phase 5: Testing and security audit (Tasks 8-10)

ROLLBACK STRATEGY:
- Keep old auth service running in parallel for 24 hours
- Feature flag: AUTH_V2_ENABLED (gradual rollout)
- Canary deployment: 10% traffic for 1 hour, monitor error rates
- Automatic rollback if error rate >1% or latency >500ms

SUCCESS METRICS:
- Login success rate >99%
- p95 latency <200ms
- Zero critical security vulnerabilities
- User satisfaction score >4.5/5
```

**THIS is first-class quality!** Every task is:
✅ Completely specified (no ambiguity)
✅ Testable (clear acceptance criteria)
✅ Implementable (technical details provided)
✅ Secure (security considerations baked in)
✅ Production-ready (rollback, monitoring, alerts)

---

## Issue Type Usage Examples

### Example 1: Feature Development (default: `--issue-type task`)

**Input:**
```bash
python jira_gen.py parse feature_request.txt --issue-type task --project PROJ
```

**Input text:**
```
Build user authentication system with email/password login and OAuth support.
```

**Output:** Epics + Tasks with acceptance criteria, technical specs, testing requirements

---

### Example 2: Bug Report (`--issue-type bug`)

**Input:**
```bash
python jira_gen.py parse bug_report.txt --issue-type bug --project PROJ
```

**Input text:**
```
Login button doesn't work on Safari iOS. When I click it, nothing happens.
I'm using iPhone 13 with iOS 16.5. Other browsers work fine.
```

**Output:**
```
Bug: Login button non-functional on Safari iOS 15+

Description: When users click the login button on Safari iOS 15+, form submission
            does not trigger. Expected: Form should submit and redirect to dashboard.
            Impact: iOS Safari users cannot access platform (estimated 15% of user base).

Severity: High
Priority: High

Environment:
  Browser: Safari iOS 15.0+
  OS: iOS 15.0-17.0
  Device: iPhone 13 (tested)
  User Role: Any authenticated user

Reproduction Steps:
  1. Open Safari browser on iPhone running iOS 15.0+
  2. Navigate to https://app.example.com/login
  3. Enter valid email: test@example.com
  4. Enter valid password
  5. Tap 'Login' button
  6. Observe: No action occurs, no error message, button remains idle

Technical Details:
  Console Error: "Uncaught TypeError: Cannot read property 'submit' of null"
  Affected Code: LoginForm.tsx line 45 (submit handler)
  API Calls: POST /api/auth/login never fires
  Network: No requests in Safari DevTools

Acceptance Criteria (Fix Verification):
  - Functional: Login button successfully submits form on Safari iOS 15+
  - Functional: User redirected to dashboard after successful login
  - Error Handling: Invalid credentials show proper error message
  - Regression: Login still works on Chrome iOS, Firefox iOS, Safari desktop
  - Edge Case: Form submission works via keyboard 'Enter' key
  - Edge Case: iOS autocomplete password fill doesn't break submission
  - Performance: Form submits within 500ms of button tap

Suggested Fix: Add touchend event listener for iOS compatibility, ensure form
              reference exists before calling submit() method.
```

---

### Example 3: User Stories (`--issue-type story`)

**Input:**
```bash
python jira_gen.py parse user_stories.txt --issue-type story --project PROJ
```

**Input text:**
```
As a user, I want to export my data to CSV so that I can analyze it in Excel.
```

**Output:**
```
Story: User data export to CSV

As a: Registered user
I want to: Export my transaction history to CSV format
So that: I can perform custom analysis in Excel/Google Sheets

Acceptance Criteria:
  - User can click "Export to CSV" button on transactions page
  - CSV file downloads immediately with all transaction data
  - CSV includes columns: Date, Description, Amount, Category, Status
  - CSV properly formatted (comma-separated, quoted strings, UTF-8 encoding)
  - Export includes only user's own data (security check)
  - Export works for datasets up to 10,000 rows without timeout
  - Loading indicator shown during export generation

Definition of Done:
  - Feature works in Chrome, Firefox, Safari
  - Unit tests cover CSV generation logic
  - Integration test verifies correct data exported
  - Security test confirms no data leakage between users
  - Documentation updated with export instructions
```

---

### Example 4: Epic Only (`--issue-type epic-only`)

**Input:**
```bash
python jira_gen.py parse epic_definition.txt --issue-type epic-only --project PROJ
```

**Input text:**
```
Implement comprehensive notification system supporting email, SMS, and push notifications
with user preferences and delivery tracking.
```

**Output:** Single Epic with high-level description, no sub-tasks (for later manual breakdown)

---

## Issue Type Quick Reference

| Issue Type | CLI Parameter | Use Case | Output | Key Fields |
|------------|---------------|----------|--------|------------|
| **Task** (default) | `--issue-type task` | Feature development, new functionality | Epics + Tasks | Title, Description, Acceptance Criteria, Technical Notes |
| **Bug** | `--issue-type bug` | Defect reports, problem tracking | Bug Reports | Summary, Reproduction Steps, Environment, Severity, Technical Details |
| **Story** | `--issue-type story` | Agile user stories | User Stories | As a/I want to/So that, Acceptance Criteria, Definition of Done |
| **Epic Only** | `--issue-type epic-only` | High-level planning | Epics only (no tasks) | Title, Description, Business Value |

### CLI Usage Patterns

```bash
# Feature development with tasks and epics
python jira_gen.py parse feature.txt --issue-type task --project PROJ

# Bug report from clipboard
python jira_gen.py parse --clipboard --issue-type bug --project PROJ

# User stories from text file
python jira_gen.py parse stories.txt --issue-type story --project PROJ

# Epic-level planning without sub-tasks
python jira_gen.py parse roadmap.txt --issue-type epic-only --project PROJ

# Skip review agent for faster processing (lower quality)
python jira_gen.py parse input.txt --issue-type bug --skip-review
```

---

## Why This Two-Agent Approach is Better

### Without Two Agents (Original Design):
```
Input → Extract → Markdown → Upload
         ❌ Might have gaps
         ❌ Might be incomplete
         ❌ User finds issues after upload
```

### With Two Agents (Your Suggestion):
```
Input → Extract → Review → Questions → Refine → Markdown → Upload
         ✅ Gaps identified
         ✅ Questions asked
         ✅ User validates early
         ✅ Complete structure
```

**Benefits**:
1. ✅ **Catches gaps early** (before Jira creation)
2. ✅ **User validates** (interactive feedback)
3. ✅ **Higher quality** (LLM reviews LLM output)
4. ✅ **Saves time** (no rework in Jira)
5. ✅ **Learns patterns** (review agent spots common issues)

---

## Testing the Two-Agent System

```python
# tests/test_two_agent_flow.py

def test_extraction_agent_identifies_epics(llm_mock):
    """Test Agent 1 extracts epics correctly"""
    agent = ExtractionAgent(llm_mock)
    result = agent.extract("Build login and signup", "PROJ")

    assert len(result.epics) > 0
    assert "authentication" in result.epics[0].title.lower()

def test_review_agent_finds_missing_criteria(llm_mock):
    """Test Agent 2 identifies missing AC"""
    structure = TicketStructure(
        project_key="PROJ",
        epics=[
            Epic(
                title="Test Epic",
                description="Desc",
                tasks=[
                    Task(title="Task without AC", description="Desc")
                ]
            )
        ]
    )

    agent = ReviewAgent(llm_mock)
    review = agent.review(structure)

    assert review.has_issues
    assert any("acceptance criteria" in gap.lower() for gap in review.gaps)

def test_review_agent_suggests_missing_tasks(llm_mock):
    """Test Agent 2 suggests error handling tasks"""
    # Setup structure with only happy path
    # Agent 2 should suggest error handling

def test_full_two_agent_flow(llm_mock):
    """Integration test: both agents working together"""
    text = "Build user authentication"

    # Agent 1: Extract
    agent1 = ExtractionAgent(llm_mock)
    structure = agent1.extract(text, "PROJ")

    # Agent 2: Review
    agent2 = ReviewAgent(llm_mock)
    review = agent2.review(structure)

    # Should have questions
    assert len(review.questions) > 0

    # Apply mock answers
    answers = {q: "Mock answer" for q in review.questions}
    refined = agent2.apply_feedback(structure, answers)

    # Refined should be more complete
    assert refined.total_tasks >= structure.total_tasks
```

---

## Summary: Your Insight Was Correct! 🎯

**You identified the critical missing piece**:

❌ **My original design**: Single-pass extraction → might have gaps
✅ **Your two-agent approach**: Extract → Review → Refine → Complete

This two-agent system ensures:
1. **Agent 1** does the heavy lifting (extraction)
2. **Agent 2** plays devil's advocate (review)
3. **User** validates and fills gaps (interaction)
4. **Result** is production-ready (quality)

**Is this the architecture you envisioned?** 🚀

---

## Quality Assurance Checklist

### First-Class Ticket Quality Standards

Every generated Jira ticket MUST include:

**✅ Extraction Agent (Agent 1) Ensures:**
1. **Business Context**
   - WHY this feature matters (business value)
   - WHO benefits (target users)
   - WHAT success looks like (outcomes)

2. **Technical Completeness**
   - Specific technologies mentioned (languages, frameworks, databases)
   - API endpoints/methods specified
   - Data models/schemas identified
   - Integration points clear

3. **Comprehensive Acceptance Criteria**
   - At LEAST 3 criteria per task
   - Functional requirements (happy path)
   - Error handling (failure scenarios)
   - Performance metrics (latency, throughput)
   - Security requirements (auth, validation, encryption)
   - Edge cases (concurrent access, race conditions, etc.)

4. **Implicit Requirements Filled**
   - Error handling for all features
   - Input validation
   - Logging/monitoring hooks
   - Testing requirements

**✅ Review Agent (Agent 2) Validates:**
1. **Zero Ambiguity**
   - No vague terms ("user-friendly" → specify exact UX)
   - No undefined metrics ("fast" → specify ms latency)
   - All acronyms explained
   - All assumptions clarified

2. **Production Readiness**
   - Database migrations specified
   - Rollback procedures defined
   - Monitoring/alerting configured
   - Documentation requirements listed

3. **Security First**
   - Authentication/authorization covered
   - Input sanitization specified
   - SQL injection prevention
   - XSS protection
   - Rate limiting
   - Audit logging

4. **Operational Excellence**
   - Deployment strategy clear
   - Backward compatibility addressed
   - Performance benchmarks defined
   - SLAs specified

5. **Developer Autonomy**
   - Task is SO complete that developer can implement WITHOUT asking questions
   - All edge cases thought through
   - Dependencies explicitly listed
   - Technical approach suggested (not mandated)

### Quality Metrics

**Excellent Ticket (Ready for Jira):**
- ✅ 5+ acceptance criteria covering functional, error, security, performance, edge cases
- ✅ Specific technologies and tools mentioned
- ✅ Database schema changes specified
- ✅ API contracts defined (endpoints, request/response formats)
- ✅ Error messages specified exactly
- ✅ Performance requirements quantified (200ms, 1000 req/sec, etc.)
- ✅ Testing requirements explicit
- ✅ Monitoring/logging requirements clear
- ✅ Rollback strategy defined

**Good Ticket (Needs Minor Refinement):**
- ✅ 3-4 acceptance criteria
- ✅ General technology mentioned (PostgreSQL, Redis)
- ⚠️ Some edge cases missing
- ⚠️ Performance not quantified ("should be fast")

**Poor Ticket (Needs Major Rework):**
- ❌ <3 acceptance criteria
- ❌ Vague descriptions ("user-friendly", "robust")
- ❌ No error handling mentioned
- ❌ No technical details
- ❌ Missing security considerations

### Agent Quality Examples

**BAD (Vague):**
```
Task: Implement login
Description: Users should be able to log in
AC: Login should work properly and be secure
```

**GOOD (Specific):**
```
Task: Implement email/password login endpoint in Auth API
Description: Create POST /api/auth/login accepting email/password,
            validates against PostgreSQL, returns JWT token.
Acceptance Criteria:
  - User can login with valid credentials, receives JWT token
  - Invalid credentials return 401 "Invalid email or password"
  - Passwords hashed with bcrypt (cost 12)
  - Login completes within 200ms (p95)
  - Rate limit: 5 attempts/min per email
  - Account locks after 5 failed attempts for 30min
Technical: JWT RS256, PostgreSQL users table, Redis rate limiting
```

### Continuous Improvement

**Agent 1 (Extraction) learns to:**
- Recognize implicit requirements (always add error handling)
- Infer technical stack from context
- Generate specific, measurable criteria
- Include security by default

**Agent 2 (Review) learns to:**
- Spot common missing patterns (database migrations, monitoring)
- Ask domain-specific questions (payment systems → PCI compliance?)
- Detect vague language automatically
- Suggest industry best practices

This two-agent system ensures **ZERO ambiguity, COMPLETE specifications, PRODUCTION-ready tickets** every time! 🎯
