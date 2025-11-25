"""
Agent 2: Review Agent

Validates ticket structure for completeness, identifies gaps,
and generates questions for user clarification.
"""

from typing import Optional, Dict, List
from models import TicketStructure, Epic, Task, Bug, UserStory
import json


class ReviewResult:
    """Results from review agent analysis"""

    def __init__(
        self,
        gaps: List[str],
        questions: List[str],
        suggestions: List[str],
        missing_tasks: List[str],
        ambiguities: List[str],
        production_readiness_concerns: Optional[List[str]] = None
    ):
        self.gaps = gaps
        self.questions = questions
        self.suggestions = suggestions
        self.missing_tasks = missing_tasks
        self.ambiguities = ambiguities
        self.production_readiness_concerns = production_readiness_concerns or []

    @property
    def has_issues(self) -> bool:
        """Check if there are any issues found"""
        return bool(
            self.gaps or
            self.questions or
            self.missing_tasks or
            self.ambiguities
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'gaps': self.gaps,
            'questions': self.questions,
            'suggestions': self.suggestions,
            'missing_tasks': self.missing_tasks,
            'ambiguities': self.ambiguities,
            'production_readiness_concerns': self.production_readiness_concerns,
            'has_issues': self.has_issues
        }

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

        if self.production_readiness_concerns:
            lines.append("\n⚠️  Production Readiness Concerns:")
            for concern in self.production_readiness_concerns:
                lines.append(f"  - {concern}")

        return "\n".join(lines) if lines else "✅ No issues found"


class ReviewAgent:
    """
    Agent 2: Review and validate ticket structure

    Responsibilities:
    - Validate completeness of extracted tickets
    - Identify missing acceptance criteria
    - Spot ambiguities and vague descriptions
    - Suggest missing tasks (error handling, testing, monitoring)
    - Generate clarifying questions for user
    - Refine structure based on user feedback
    """

    def __init__(self, llm_client: Optional[object] = None):
        """
        Initialize review agent

        Args:
            llm_client: OpenAI/Anthropic client (optional)
        """
        self.llm_client = llm_client

    def review(self, structure: TicketStructure) -> ReviewResult:
        """
        Review ticket structure for completeness and quality

        Args:
            structure: Ticket structure to review

        Returns:
            ReviewResult with gaps, questions, and suggestions
        """
        if self.llm_client:
            return self._review_with_llm(structure)
        else:
            return self._review_simple(structure)

    def _review_with_llm(self, structure: TicketStructure) -> ReviewResult:
        """Use LLM to perform comprehensive review"""
        from .prompts import REVIEW_PROMPT

        # Convert structure to text for review
        structure_text = self._structure_to_text(structure)

        from config import config

        prompt = REVIEW_PROMPT.format(structure=structure_text)

        # Call LLM (OpenAI or Ollama)
        if hasattr(self.llm_client, 'chat'):
            # Determine model to use
            if config.llm_provider == 'ollama':
                model = config.ollama_model
                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior software architect reviewing requirements. "
                                     "Find gaps, ambiguities, and missing details. Be thorough and critical."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5
                )
            else:
                model = config.llm_model
                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior software architect reviewing requirements. "
                                     "Find gaps, ambiguities, and missing details. Be thorough and critical."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.5
                )
            content = response.choices[0].message.content
        # Call LLM (Anthropic)
        else:
            response = self.llm_client.messages.create(
                model=config.llm_model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            content = response.content[0].text

        # Parse review results
        try:
            review_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return self._review_simple(structure)

        return ReviewResult(
            gaps=review_data.get('gaps', []),
            questions=review_data.get('questions', []),
            suggestions=review_data.get('suggestions', []),
            missing_tasks=review_data.get('missing_tasks', []),
            ambiguities=review_data.get('ambiguities', []),
            production_readiness_concerns=review_data.get('production_readiness_concerns', [])
        )

    def _review_simple(self, structure: TicketStructure) -> ReviewResult:
        """Simple rule-based review without LLM"""
        gaps = []
        questions = []
        suggestions = []

        # Check tasks for missing acceptance criteria
        for epic in structure.epics:
            for task in epic.tasks:
                if not task.acceptance_criteria:
                    gaps.append(f"Task '{task.title}' has no acceptance criteria")
                    questions.append(f"What are the success criteria for '{task.title}'?")
                elif len(task.acceptance_criteria) < 3:
                    gaps.append(f"Task '{task.title}' has only {len(task.acceptance_criteria)} acceptance criteria (recommend ≥3)")
                    questions.append(f"Can you provide more detailed acceptance criteria for '{task.title}'?")

                # Check for vague descriptions
                vague_words = ['user-friendly', 'fast', 'robust', 'good', 'nice', 'clean']
                desc_lower = task.description.lower()
                for word in vague_words:
                    if word in desc_lower:
                        gaps.append(f"Task '{task.title}' contains vague term '{word}'")
                        questions.append(f"Can you be more specific about '{word}' in '{task.title}'?")

        # Check bugs for reproduction steps
        for bug in structure.bugs:
            if not bug.reproduction_steps or len(bug.reproduction_steps) < 3:
                gaps.append(f"Bug '{bug.summary}' needs detailed reproduction steps (≥3 steps)")
                questions.append(f"What are the exact steps to reproduce '{bug.summary}'?")

            if not bug.environment or not (bug.environment.browser or bug.environment.os):
                gaps.append(f"Bug '{bug.summary}' missing environment details")
                questions.append(f"What browser/OS/device was '{bug.summary}' found on?")

        # Check stories for acceptance criteria
        for story in structure.stories:
            if not story.acceptance_criteria or len(story.acceptance_criteria) < 3:
                gaps.append(f"Story '{story.title}' needs detailed acceptance criteria (≥3)")
                questions.append(f"What are the acceptance criteria for '{story.title}'?")

        # Suggest common missing tasks
        if structure.epics:
            suggestions.append("Consider adding error handling tasks for each feature")
            suggestions.append("Consider adding unit/integration testing tasks")
            suggestions.append("Consider adding monitoring/logging tasks for production")

        return ReviewResult(
            gaps=gaps,
            questions=questions,
            suggestions=suggestions,
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
            structure: Original ticket structure
            user_answers: Dict mapping questions to user answers

        Returns:
            Improved ticket structure
        """
        if self.llm_client:
            return self._apply_feedback_with_llm(structure, user_answers)
        else:
            # Without LLM, return original structure
            return structure

    def _apply_feedback_with_llm(
        self,
        structure: TicketStructure,
        user_answers: Dict[str, str]
    ) -> TicketStructure:
        """Use LLM to apply user feedback and refine structure"""
        from .prompts import REFINEMENT_PROMPT

        structure_text = self._structure_to_text(structure)
        answers_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in user_answers.items())

        from config import config

        prompt = REFINEMENT_PROMPT.format(
            structure=structure_text,
            feedback=answers_text
        )

        # Call LLM (OpenAI or Ollama)
        if hasattr(self.llm_client, 'chat'):
            # Determine model to use
            if config.llm_provider == 'ollama':
                model = config.ollama_model
                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a requirements analyst. Refine the ticket structure based on user feedback."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
            else:
                model = config.llm_model
                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a requirements analyst. Refine the ticket structure based on user feedback."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
            content = response.choices[0].message.content
        # Call LLM (Anthropic)
        else:
            response = self.llm_client.messages.create(
                model=config.llm_model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.content[0].text

        # Parse refined structure
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: return original structure
            return structure

        # Use ExtractionAgent's parser to convert JSON to models
        from .extraction_agent import ExtractionAgent
        agent = ExtractionAgent()
        return agent._parse_llm_response(data, structure.project_key, structure.issue_type)

    def _structure_to_text(self, structure: TicketStructure) -> str:
        """Convert ticket structure to readable text for LLM review"""
        lines = [f"Project: {structure.project_key}"]
        lines.append(f"Issue Type: {structure.issue_type}\n")

        # Format epics and tasks
        for epic in structure.epics:
            lines.append(f"\nEpic: {epic.title}")
            lines.append(f"Description: {epic.description}")
            if epic.business_value:
                lines.append(f"Business Value: {epic.business_value}")
            lines.append(f"Priority: {epic.priority}")

            for task in epic.tasks:
                lines.append(f"\n  Task: {task.title}")
                lines.append(f"  Description: {task.description}")
                lines.append(f"  Priority: {task.priority}")
                if task.estimated_effort:
                    lines.append(f"  Estimated Effort: {task.estimated_effort}")

                if task.acceptance_criteria:
                    lines.append("  Acceptance Criteria:")
                    for ac in task.acceptance_criteria:
                        lines.append(f"    - {ac}")

                if task.technical_notes:
                    lines.append(f"  Technical Notes: {task.technical_notes}")

        # Format bugs
        for bug in structure.bugs:
            lines.append(f"\nBug: {bug.summary}")
            lines.append(f"Description: {bug.description}")
            lines.append(f"Severity: {bug.severity}")
            lines.append(f"Priority: {bug.priority}")

            if bug.reproduction_steps:
                lines.append("Reproduction Steps:")
                for i, step in enumerate(bug.reproduction_steps, 1):
                    lines.append(f"  {i}. {step}")

            if bug.environment:
                lines.append("Environment:")
                if bug.environment.browser:
                    lines.append(f"  Browser: {bug.environment.browser}")
                if bug.environment.os:
                    lines.append(f"  OS: {bug.environment.os}")

            if bug.acceptance_criteria:
                lines.append("Fix Verification Criteria:")
                for ac in bug.acceptance_criteria:
                    lines.append(f"  - {ac}")

        # Format user stories
        for story in structure.stories:
            lines.append(f"\nStory: {story.title}")
            lines.append(f"As a: {story.as_a}")
            lines.append(f"I want to: {story.i_want_to}")
            lines.append(f"So that: {story.so_that}")
            lines.append(f"Priority: {story.priority}")

            if story.acceptance_criteria:
                lines.append("Acceptance Criteria:")
                for ac in story.acceptance_criteria:
                    lines.append(f"  - {ac}")

            if story.definition_of_done:
                lines.append("Definition of Done:")
                for dod in story.definition_of_done:
                    lines.append(f"  - {dod}")

        return "\n".join(lines)
