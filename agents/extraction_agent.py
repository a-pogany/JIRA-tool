"""
Agent 1: Extraction Agent

Extracts structured tickets (Epics/Tasks, Bugs, or Stories) from unstructured text
"""

import json
from typing import Optional
from models import TicketStructure, IssueType
from agents.prompts import EXTRACTION_PROMPT, BUG_EXTRACTION_PROMPT, STORY_EXTRACTION_PROMPT


class ExtractionAgent:
    """
    Agent 1: Extract epics, tasks, bugs, or stories from text

    Responsibilities:
    - Identify issue structure based on type (task/bug/story/epic-only)
    - Extract appropriate fields for each issue type
    - Extract acceptance criteria or reproduction steps
    - Detect priorities and severity
    - Add implicit requirements (security, performance, testing)
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
        Extract structured tickets from text

        Args:
            text: Input text (meeting notes, bug description, etc.)
            project_key: Jira project key (e.g., "PROJ")

        Returns:
            TicketStructure with extracted tickets
        """
        if self.llm_client:
            return self._extract_with_llm(text, project_key)
        else:
            return self._extract_simple(text, project_key)

    def _extract_with_llm(self, text: str, project_key: str) -> TicketStructure:
        """
        Extract using LLM (OpenAI, Anthropic, or Ollama)

        Args:
            text: Input text
            project_key: Jira project key

        Returns:
            TicketStructure with extracted tickets
        """
        from config import config

        # Select prompt based on issue type
        if self.issue_type == 'bug':
            prompt = BUG_EXTRACTION_PROMPT.format(text=text, project_key=project_key)
        elif self.issue_type == 'story':
            prompt = STORY_EXTRACTION_PROMPT.format(text=text, project_key=project_key)
        else:  # task or epic-only
            prompt = EXTRACTION_PROMPT.format(text=text, project_key=project_key)

        # Call LLM based on provider type
        try:
            if hasattr(self.llm_client, 'chat'):  # OpenAI or Ollama
                # Determine model to use
                if config.llm_provider == 'ollama':
                    model = config.ollama_model
                    # Ollama may not support response_format, so we'll handle JSON parsing more carefully
                    response = self.llm_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a technical product manager extracting Jira tickets from text. Return valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                else:
                    model = config.llm_model
                    response = self.llm_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a technical product manager extracting Jira tickets from text. Return valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                json_text = response.choices[0].message.content

            elif hasattr(self.llm_client, 'messages'):  # Anthropic
                response = self.llm_client.messages.create(
                    model=config.llm_model,
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                json_text = response.content[0].text

            else:
                raise ValueError("Unknown LLM client type")

            # Parse JSON response
            data = json.loads(json_text)

            # Use helper method to parse JSON into Pydantic models
            return self._parse_llm_response(data, project_key, self.issue_type)

        except Exception as e:
            print(f"LLM extraction failed: {e}")
            print("Falling back to simple extraction...")
            return self._extract_simple(text, project_key)

    def _extract_simple(self, text: str, project_key: str) -> TicketStructure:
        """
        Simple extraction without LLM (fallback mode)

        Creates basic structure from text patterns
        """
        from models import Epic, Task

        structure = TicketStructure(
            project_key=project_key,
            issue_type=self.issue_type
        )

        # Simple pattern: create one epic from the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if lines:
            epic = Epic(
                title=lines[0][:200] if lines else "Extracted Feature",
                description=text[:1000],
                business_value="To be refined",
                priority="Medium",
                tasks=[
                    Task(
                        title="Implement " + lines[0][:150] if lines else "Implementation task",
                        description=text[:500],
                        acceptance_criteria=[
                            "Feature works as described",
                            "Tests pass",
                            "Documentation updated"
                        ],
                        priority="Medium"
                    )
                ]
            )
            structure.epics = [epic]

        return structure

    def _parse_llm_response(self, data: dict, project_key: str, issue_type: str) -> TicketStructure:
        """
        Parse LLM JSON response into Pydantic models

        Args:
            data: JSON dict from LLM
            project_key: Jira project key
            issue_type: Issue type (task, bug, story, epic-only)

        Returns:
            TicketStructure with properly typed models
        """
        from models import Epic, Bug, UserStory

        structure = TicketStructure(
            project_key=project_key,
            issue_type=issue_type
        )

        # Populate based on issue type - parse dicts into Pydantic models
        if issue_type == 'bug':
            structure.bugs = [Bug(**bug_data) for bug_data in data.get('bugs', [])]
        elif issue_type == 'story':
            structure.stories = [UserStory(**story_data) for story_data in data.get('stories', [])]
        else:  # task or epic-only
            structure.epics = [Epic(**epic_data) for epic_data in data.get('epics', [])]

        return structure
