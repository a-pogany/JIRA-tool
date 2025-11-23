# JIRA Ticket Generator - Two-Agent Design Specification

## Design Philosophy

Your insight is correct - we need **TWO intelligent agents**:

1. **Extraction Agent**: Breaks down text into structured tasks
2. **Review Agent**: Validates completeness, spots gaps, asks clarifying questions

This ensures high-quality output before creating Jira tickets.

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

## Agent 1: Extraction Agent

**Purpose**: Extract structured tasks from unstructured text

```python
# agents/extraction_agent.py
from models import TicketStructure, Epic, Task
from typing import Optional

class ExtractionAgent:
    """
    Agent 1: Extract epics and tasks from text

    Responsibilities:
    - Identify main features/epics
    - Break down into tasks
    - Extract acceptance criteria
    - Detect priorities from language
    """

    def __init__(self, llm_client: Optional[object] = None):
        """
        Args:
            llm_client: OpenAI/Anthropic client (optional)
        """
        self.llm_client = llm_client

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
