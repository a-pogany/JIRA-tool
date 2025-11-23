"""
Jira API Client

Handles uploading tickets to Jira via REST API
"""

import requests
from typing import List, Dict, Optional
from models import TicketStructure, Epic, Task, Bug, UserStory


class JiraClient:
    """Client for interacting with Jira REST API"""

    def __init__(self, jira_url: str, email: str, api_token: str):
        """
        Initialize Jira client

        Args:
            jira_url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            email: User email for authentication
            api_token: Jira API token
        """
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = (email, api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_connection(self) -> bool:
        """
        Test Jira API connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.jira_url}/rest/api/3/myself",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def upload_structure(self, structure: TicketStructure) -> Dict[str, List[str]]:
        """
        Upload entire ticket structure to Jira

        Args:
            structure: TicketStructure to upload

        Returns:
            Dict with created ticket keys:
            {
                'epics': ['PROJ-1', 'PROJ-2'],
                'tasks': ['PROJ-3', 'PROJ-4'],
                'bugs': ['PROJ-5'],
                'stories': ['PROJ-6']
            }
        """
        results = {
            'epics': [],
            'tasks': [],
            'bugs': [],
            'stories': []
        }

        # Upload epics and tasks
        for epic in structure.epics:
            epic_key = self.create_epic(epic, structure.project_key)
            if epic_key:
                results['epics'].append(epic_key)

                # Upload tasks under epic
                for task in epic.tasks:
                    task_key = self.create_task(task, structure.project_key, epic_key)
                    if task_key:
                        results['tasks'].append(task_key)

        # Upload bugs
        for bug in structure.bugs:
            bug_key = self.create_bug(bug, structure.project_key)
            if bug_key:
                results['bugs'].append(bug_key)

        # Upload stories
        for story in structure.stories:
            story_key = self.create_story(story, structure.project_key)
            if story_key:
                results['stories'].append(story_key)

        return results

    def create_epic(self, epic: Epic, project_key: str) -> Optional[str]:
        """
        Create epic in Jira

        Args:
            epic: Epic model
            project_key: Jira project key

        Returns:
            Created epic key (e.g., 'PROJ-123') or None if failed
        """
        description = epic.description
        if epic.business_value:
            description += f"\n\n**Business Value**: {epic.business_value}"

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": epic.title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Epic"},
                "priority": {"name": epic.priority}
            }
        }

        return self._create_issue(payload)

    def create_task(self, task: Task, project_key: str, epic_key: Optional[str] = None) -> Optional[str]:
        """
        Create task in Jira

        Args:
            task: Task model
            project_key: Jira project key
            epic_key: Parent epic key (optional)

        Returns:
            Created task key or None if failed
        """
        # Build description with acceptance criteria
        description_parts = [task.description]

        if task.acceptance_criteria:
            description_parts.append("\n\n**Acceptance Criteria**:")
            for ac in task.acceptance_criteria:
                description_parts.append(f"- {ac}")

        if task.technical_notes:
            description_parts.append(f"\n\n**Technical Notes**: {task.technical_notes}")

        description = "\n".join(description_parts)

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": task.title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"},
                "priority": {"name": task.priority}
            }
        }

        # Link to epic if provided
        if epic_key:
            payload["fields"]["parent"] = {"key": epic_key}

        return self._create_issue(payload)

    def create_bug(self, bug: Bug, project_key: str) -> Optional[str]:
        """
        Create bug in Jira

        Args:
            bug: Bug model
            project_key: Jira project key

        Returns:
            Created bug key or None if failed
        """
        # Build comprehensive description
        description_parts = [bug.description]

        if bug.reproduction_steps:
            description_parts.append("\n\n**Reproduction Steps**:")
            for i, step in enumerate(bug.reproduction_steps, 1):
                description_parts.append(f"{i}. {step}")

        if bug.environment:
            env = bug.environment
            description_parts.append("\n\n**Environment**:")
            if env.browser:
                description_parts.append(f"- Browser: {env.browser}")
            if env.os:
                description_parts.append(f"- OS: {env.os}")
            if env.device:
                description_parts.append(f"- Device: {env.device}")

        if bug.technical_details and bug.technical_details.error_message:
            description_parts.append(f"\n\n**Error**: {bug.technical_details.error_message}")

        if bug.acceptance_criteria:
            description_parts.append("\n\n**Fix Verification**:")
            for ac in bug.acceptance_criteria:
                description_parts.append(f"- {ac}")

        description = "\n".join(description_parts)

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": bug.summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Bug"},
                "priority": {"name": bug.priority}
            }
        }

        return self._create_issue(payload)

    def create_story(self, story: UserStory, project_key: str) -> Optional[str]:
        """
        Create user story in Jira

        Args:
            story: UserStory model
            project_key: Jira project key

        Returns:
            Created story key or None if failed
        """
        # Build description in user story format
        description_parts = [
            f"**As a**: {story.as_a}",
            f"**I want to**: {story.i_want_to}",
            f"**So that**: {story.so_that}"
        ]

        if story.acceptance_criteria:
            description_parts.append("\n**Acceptance Criteria**:")
            for ac in story.acceptance_criteria:
                description_parts.append(f"- {ac}")

        if story.definition_of_done:
            description_parts.append("\n**Definition of Done**:")
            for dod in story.definition_of_done:
                description_parts.append(f"- {dod}")

        description = "\n".join(description_parts)

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": story.title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Story"},
                "priority": {"name": story.priority}
            }
        }

        # Add story points if provided
        if story.story_points:
            payload["fields"]["customfield_10016"] = story.story_points  # Story points field

        return self._create_issue(payload)

    def _create_issue(self, payload: dict) -> Optional[str]:
        """
        Create issue in Jira via REST API

        Args:
            payload: Issue creation payload

        Returns:
            Created issue key or None if failed
        """
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                json=payload,
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 201:
                return response.json()['key']
            else:
                print(f"Failed to create issue: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
