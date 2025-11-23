"""
Markdown generation and parsing utilities

Handles conversion between TicketStructure and markdown files
"""

from pathlib import Path
from datetime import datetime
from typing import List
from models import TicketStructure, Epic, Task, Bug, UserStory


def write_markdown(structure: TicketStructure, output_path: Path) -> None:
    """
    Write ticket structure to markdown file

    Args:
        structure: Ticket structure to convert
        output_path: Path to output markdown file
    """
    lines = []

    # Header
    lines.append(f"# JIRA Tickets - {structure.project_key}")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Issue Type**: {structure.issue_type}")
    lines.append(f"\n---\n")

    # Format based on issue type
    if structure.issue_type in ['task', 'epic-only']:
        lines.extend(_format_epics(structure.epics))
    elif structure.issue_type == 'bug':
        lines.extend(_format_bugs(structure.bugs))
    elif structure.issue_type == 'story':
        lines.extend(_format_stories(structure.stories))

    # Write to file
    output_path.write_text('\n'.join(lines), encoding='utf-8')


def _format_epics(epics: List[Epic]) -> List[str]:
    """Format epics and tasks as markdown"""
    lines = []

    for i, epic in enumerate(epics, 1):
        lines.append(f"## Epic {i}: {epic.title}\n")
        lines.append(f"**Description**: {epic.description}\n")

        if epic.business_value:
            lines.append(f"**Business Value**: {epic.business_value}\n")

        lines.append(f"**Priority**: {epic.priority}\n")

        # Tasks
        if epic.tasks:
            lines.append(f"\n### Tasks ({len(epic.tasks)})\n")

            for j, task in enumerate(epic.tasks, 1):
                lines.append(f"#### Task {i}.{j}: {task.title}\n")
                lines.append(f"**Description**: {task.description}\n")
                lines.append(f"**Priority**: {task.priority}")

                if task.estimated_effort:
                    lines.append(f" | **Effort**: {task.estimated_effort}")
                lines.append("\n")

                # Acceptance Criteria
                if task.acceptance_criteria:
                    lines.append("**Acceptance Criteria**:")
                    for ac in task.acceptance_criteria:
                        lines.append(f"- {ac}")
                    lines.append("")

                # Technical Notes
                if task.technical_notes:
                    lines.append(f"**Technical Notes**: {task.technical_notes}\n")

                lines.append("---\n")

        lines.append("\n")

    return lines


def _format_bugs(bugs: List[Bug]) -> List[str]:
    """Format bug reports as markdown"""
    lines = []

    for i, bug in enumerate(bugs, 1):
        lines.append(f"## Bug {i}: {bug.summary}\n")
        lines.append(f"**Description**: {bug.description}\n")
        lines.append(f"**Severity**: {bug.severity} | **Priority**: {bug.priority}\n")

        # Reproduction Steps
        if bug.reproduction_steps:
            lines.append("\n**Reproduction Steps**:")
            for j, step in enumerate(bug.reproduction_steps, 1):
                lines.append(f"{j}. {step}")
            lines.append("")

        # Environment
        if bug.environment:
            lines.append("**Environment**:")
            env = bug.environment
            if env.browser:
                lines.append(f"- Browser: {env.browser}")
            if env.os:
                lines.append(f"- OS: {env.os}")
            if env.device:
                lines.append(f"- Device: {env.device}")
            if env.user_role:
                lines.append(f"- User Role: {env.user_role}")
            if env.data_conditions:
                lines.append(f"- Data Conditions: {env.data_conditions}")
            lines.append("")

        # Technical Details
        if bug.technical_details:
            lines.append("**Technical Details**:")
            tech = bug.technical_details
            if tech.error_message:
                lines.append(f"- Error: {tech.error_message}")
            if tech.console_logs:
                lines.append(f"- Console: {tech.console_logs}")
            if tech.affected_code:
                lines.append(f"- Code: {tech.affected_code}")
            if tech.api_calls:
                lines.append(f"- API: {tech.api_calls}")
            if tech.stack_trace:
                lines.append(f"- Stack Trace: {tech.stack_trace}")
            lines.append("")

        # Fix Verification Criteria
        if bug.acceptance_criteria:
            lines.append("**Fix Verification Criteria**:")
            for ac in bug.acceptance_criteria:
                lines.append(f"- {ac}")
            lines.append("")

        # Suggested Fix
        if bug.suggested_fix:
            lines.append(f"**Suggested Fix**: {bug.suggested_fix}\n")

        lines.append("---\n")

    return lines


def _format_stories(stories: List[UserStory]) -> List[str]:
    """Format user stories as markdown"""
    lines = []

    for i, story in enumerate(stories, 1):
        lines.append(f"## Story {i}: {story.title}\n")

        # User Story Format
        lines.append("**User Story**:")
        lines.append(f"- **As a**: {story.as_a}")
        lines.append(f"- **I want to**: {story.i_want_to}")
        lines.append(f"- **So that**: {story.so_that}\n")

        lines.append(f"**Priority**: {story.priority}")
        if story.estimated_effort:
            lines.append(f" | **Effort**: {story.estimated_effort}")
        lines.append("\n")

        # Acceptance Criteria
        if story.acceptance_criteria:
            lines.append("**Acceptance Criteria**:")
            for ac in story.acceptance_criteria:
                lines.append(f"- {ac}")
            lines.append("")

        # Technical Notes
        if story.technical_notes:
            lines.append(f"**Technical Notes**: {story.technical_notes}\n")

        lines.append("---\n")

    return lines


def read_markdown(markdown_path: Path) -> str:
    """
    Read markdown file and return content

    Args:
        markdown_path: Path to markdown file

    Returns:
        Markdown content as string
    """
    return markdown_path.read_text(encoding='utf-8')


def list_markdown_files(directory: Path = Path('.')) -> List[Path]:
    """
    List all markdown files in directory

    Args:
        directory: Directory to search (default: current directory)

    Returns:
        List of markdown file paths, sorted by modification time (newest first)
    """
    md_files = list(directory.glob('jira_tickets_*.md'))
    # Sort by modification time, newest first
    md_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return md_files


def generate_filename(project_key: str, issue_type: str = 'task') -> str:
    """
    Generate timestamped filename for markdown output

    Args:
        project_key: Jira project key
        issue_type: Issue type

    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"jira_tickets_{project_key}_{issue_type}_{timestamp}.md"
