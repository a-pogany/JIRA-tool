"""
Markdown parsing utilities - Convert markdown back to TicketStructure

Parses generated markdown files back into TicketStructure for JIRA upload
"""

from pathlib import Path
from typing import List
from models import (
    TicketStructure, Epic, Task, Bug, UserStory,
    Environment, TechnicalDetails
)
import re


def parse_markdown(markdown_path: Path) -> TicketStructure:
    """
    Parse markdown file back to TicketStructure

    Args:
        markdown_path: Path to markdown file

    Returns:
        TicketStructure object
    """
    content = markdown_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Extract project key and issue type from header
    project_key = None
    issue_type = 'task'

    for line in lines[:10]:
        if line.startswith('# JIRA Tickets - '):
            project_key = line.replace('# JIRA Tickets - ', '').strip()
        elif line.startswith('**Issue Type**:'):
            issue_type = line.replace('**Issue Type**:', '').strip().lower()

    if not project_key:
        raise ValueError("Could not extract project key from markdown")

    # Parse based on issue type
    if issue_type in ['task', 'epic-only']:
        epics = _parse_epics_from_markdown(content)
        return TicketStructure(
            project_key=project_key,
            issue_type=issue_type,
            epics=epics
        )
    elif issue_type == 'bug':
        bugs = _parse_bugs_from_markdown(content)
        return TicketStructure(
            project_key=project_key,
            issue_type=issue_type,
            bugs=bugs
        )
    elif issue_type == 'story':
        stories = _parse_stories_from_markdown(content)
        return TicketStructure(
            project_key=project_key,
            issue_type=issue_type,
            stories=stories
        )
    else:
        raise ValueError(f"Unsupported issue type: {issue_type}")


def _parse_epics_from_markdown(content: str) -> List[Epic]:
    """Parse epics and tasks from markdown"""
    epics = []
    epic_sections = re.split(r'\n## Epic \d+:', content)[1:]  # Skip header

    for section in epic_sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        # Extract epic title (first line)
        epic_title = lines[0].strip()

        # Extract epic fields
        description = ''
        business_value = None
        priority = 'Medium'

        for line in lines[1:]:
            if line.startswith('**Description**:'):
                description = line.replace('**Description**:', '').strip()
            elif line.startswith('**Business Value**:'):
                business_value = line.replace('**Business Value**:', '').strip()
            elif line.startswith('**Priority**:'):
                # Extract only the priority value, ignore anything after |
                priority_line = line.replace('**Priority**:', '').strip()
                if '|' in priority_line:
                    priority = priority_line.split('|')[0].strip()
                else:
                    priority = priority_line

        # Parse tasks
        tasks = []
        task_sections = re.split(r'\n#### Task \d+\.\d+:', section)

        for task_section in task_sections[1:]:  # Skip first (epic header)
            task_lines = task_section.strip().split('\n')
            if not task_lines:
                continue

            task_title = task_lines[0].strip()
            task_description = ''
            task_priority = 'Medium'
            task_effort = None
            acceptance_criteria = []
            technical_notes = None

            i = 1
            while i < len(task_lines):
                line = task_lines[i]

                if line.startswith('**Description**:'):
                    task_description = line.replace('**Description**:', '').strip()
                elif line.startswith('**Priority**:'):
                    # Handle "Priority: High | Effort: Medium" format
                    priority_line = line.replace('**Priority**:', '').strip()
                    if '|' in priority_line:
                        parts = priority_line.split('|')
                        task_priority = parts[0].strip()
                        if len(parts) > 1 and '**Effort**:' in parts[1]:
                            task_effort = parts[1].replace('**Effort**:', '').strip()
                    else:
                        task_priority = priority_line
                elif line.startswith('**Acceptance Criteria**:'):
                    # Collect all bullet points
                    i += 1
                    while i < len(task_lines) and task_lines[i].strip().startswith('-'):
                        acceptance_criteria.append(task_lines[i].strip()[2:])
                        i += 1
                    i -= 1  # Back up one
                elif line.startswith('**Technical Notes**:'):
                    technical_notes = line.replace('**Technical Notes**:', '').strip()

                i += 1

            if task_title and task_description:
                tasks.append(Task(
                    title=task_title,
                    description=task_description,
                    acceptance_criteria=acceptance_criteria,
                    technical_notes=technical_notes,
                    priority=task_priority,
                    estimated_effort=task_effort
                ))

        if epic_title and description:
            epics.append(Epic(
                title=epic_title,
                description=description,
                business_value=business_value,
                priority=priority,
                tasks=tasks
            ))

    return epics


def _parse_bugs_from_markdown(content: str) -> List[Bug]:
    """Parse bug reports from markdown"""
    bugs = []
    bug_sections = re.split(r'\n## Bug \d+:', content)[1:]

    for section in bug_sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        summary = lines[0].strip()
        description = ''
        severity = 'Medium'
        priority = 'Medium'
        reproduction_steps = []
        environment = Environment()
        technical_details = None
        acceptance_criteria = []
        suggested_fix = None

        i = 1
        while i < len(lines):
            line = lines[i]

            if line.startswith('**Description**:'):
                description = line.replace('**Description**:', '').strip()
            elif line.startswith('**Severity**:'):
                # Handle "Severity: High | Priority: Critical" format
                sev_line = line.replace('**Severity**:', '').strip()
                if '|' in sev_line:
                    parts = sev_line.split('|')
                    severity = parts[0].strip()
                    if len(parts) > 1 and '**Priority**:' in parts[1]:
                        priority = parts[1].replace('**Priority**:', '').strip()
                else:
                    severity = sev_line
            elif line.startswith('**Reproduction Steps**:'):
                i += 1
                while i < len(lines) and re.match(r'^\d+\.', lines[i].strip()):
                    step = re.sub(r'^\d+\.\s*', '', lines[i].strip())
                    reproduction_steps.append(step)
                    i += 1
                i -= 1
            elif line.startswith('**Environment**:'):
                i += 1
                env_dict = {}
                while i < len(lines) and lines[i].strip().startswith('-'):
                    env_line = lines[i].strip()[2:]
                    if ':' in env_line:
                        key, value = env_line.split(':', 1)
                        env_dict[key.strip().lower().replace(' ', '_')] = value.strip()
                    i += 1
                i -= 1
                environment = Environment(**env_dict)
            elif line.startswith('**Technical Details**:'):
                i += 1
                tech_dict = {}
                while i < len(lines) and lines[i].strip().startswith('-'):
                    tech_line = lines[i].strip()[2:]
                    if ':' in tech_line:
                        key, value = tech_line.split(':', 1)
                        key_map = {
                            'error': 'error_message',
                            'console': 'console_logs',
                            'code': 'affected_code',
                            'api': 'api_calls',
                            'stack trace': 'stack_trace'
                        }
                        mapped_key = key_map.get(key.strip().lower(), key.strip().lower().replace(' ', '_'))
                        tech_dict[mapped_key] = value.strip()
                    i += 1
                i -= 1
                technical_details = TechnicalDetails(**tech_dict)
            elif line.startswith('**Fix Verification Criteria**:'):
                i += 1
                while i < len(lines) and lines[i].strip().startswith('-'):
                    acceptance_criteria.append(lines[i].strip()[2:])
                    i += 1
                i -= 1
            elif line.startswith('**Suggested Fix**:'):
                suggested_fix = line.replace('**Suggested Fix**:', '').strip()

            i += 1

        if summary and description and len(reproduction_steps) >= 3:
            bugs.append(Bug(
                summary=summary,
                description=description,
                severity=severity,
                priority=priority,
                reproduction_steps=reproduction_steps,
                environment=environment,
                technical_details=technical_details,
                acceptance_criteria=acceptance_criteria,
                suggested_fix=suggested_fix
            ))

    return bugs


def _parse_stories_from_markdown(content: str) -> List[UserStory]:
    """Parse user stories from markdown"""
    stories = []
    story_sections = re.split(r'\n## Story \d+:', content)[1:]

    for section in story_sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        title = lines[0].strip()
        as_a = ''
        i_want_to = ''
        so_that = ''
        priority = 'Medium'
        estimated_effort = None
        acceptance_criteria = []
        technical_notes = None

        i = 1
        while i < len(lines):
            line = lines[i]

            if '**As a**:' in line:
                as_a = line.split('**As a**:')[1].strip()
            elif '**I want to**:' in line:
                i_want_to = line.split('**I want to**:')[1].strip()
            elif '**So that**:' in line:
                so_that = line.split('**So that**:')[1].strip()
            elif line.startswith('**Priority**:'):
                priority_line = line.replace('**Priority**:', '').strip()
                if '|' in priority_line:
                    parts = priority_line.split('|')
                    priority = parts[0].strip()
                    if len(parts) > 1 and '**Effort**:' in parts[1]:
                        estimated_effort = parts[1].replace('**Effort**:', '').strip()
                else:
                    priority = priority_line
            elif line.startswith('**Acceptance Criteria**:'):
                i += 1
                while i < len(lines) and lines[i].strip().startswith('-'):
                    acceptance_criteria.append(lines[i].strip()[2:])
                    i += 1
                i -= 1
            elif line.startswith('**Technical Notes**:'):
                technical_notes = line.replace('**Technical Notes**:', '').strip()

            i += 1

        if title and as_a and i_want_to and so_that and len(acceptance_criteria) >= 3:
            stories.append(UserStory(
                title=title,
                as_a=as_a,
                i_want_to=i_want_to,
                so_that=so_that,
                acceptance_criteria=acceptance_criteria,
                priority=priority,
                estimated_effort=estimated_effort,
                technical_notes=technical_notes
            ))

    return stories
