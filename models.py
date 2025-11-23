"""
Data models for JIRA Ticket Generator

Supports multiple issue types:
- task: Epics + Tasks for feature development
- bug: Bug/Problem Reports
- story: User Stories
- epic-only: High-level Epics without sub-tasks
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Type definitions
IssueType = Literal['task', 'bug', 'story', 'epic-only']
Priority = Literal['Critical', 'High', 'Medium', 'Low']
Severity = Literal['Critical', 'High', 'Medium', 'Low']
EffortSize = Literal['Small', 'Medium', 'Large']


# ═══════════════════════════════════════════════════════
# TASK/EPIC MODELS (for feature development)
# ═══════════════════════════════════════════════════════

class Task(BaseModel):
    """Individual task (sub-task of Epic)"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    technical_notes: Optional[str] = None
    priority: Priority = 'Medium'
    estimated_effort: Optional[EffortSize] = None


class Epic(BaseModel):
    """Epic (high-level feature/initiative)"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str
    business_value: Optional[str] = None
    priority: Priority = 'Medium'
    tasks: List[Task] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════
# BUG REPORT MODELS
# ═══════════════════════════════════════════════════════

class Environment(BaseModel):
    """Environment where bug occurs"""
    browser: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    version: Optional[str] = None
    user_role: Optional[str] = None
    data_conditions: Optional[str] = None


class TechnicalDetails(BaseModel):
    """Technical details about the bug"""
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    console_logs: Optional[str] = None
    affected_code: Optional[str] = None
    api_calls: Optional[str] = None
    database_state: Optional[str] = None


class Bug(BaseModel):
    """Bug/Problem report"""
    summary: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=20)
    severity: Severity = 'Medium'
    priority: Priority = 'Medium'
    reproduction_steps: List[str] = Field(..., min_items=3)
    environment: Environment = Field(default_factory=Environment)
    technical_details: Optional[TechnicalDetails] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    suggested_fix: Optional[str] = None


# ═══════════════════════════════════════════════════════
# USER STORY MODELS
# ═══════════════════════════════════════════════════════

class UserStory(BaseModel):
    """Agile user story"""
    title: str = Field(..., min_length=10, max_length=200)
    as_a: str = Field(..., min_length=5)  # Role/persona
    i_want_to: str = Field(..., min_length=10)  # Action/feature
    so_that: str = Field(..., min_length=10)  # Business value/benefit
    acceptance_criteria: List[str] = Field(..., min_items=3)
    priority: Priority = 'Medium'
    estimated_effort: Optional[EffortSize] = None
    technical_notes: Optional[str] = None


# ═══════════════════════════════════════════════════════
# UNIFIED CONTAINER
# ═══════════════════════════════════════════════════════

class TicketStructure(BaseModel):
    """Container for all extracted tickets"""
    project_key: str = Field(..., pattern=r'^[A-Z][A-Z0-9]{1,9}$')
    issue_type: IssueType = 'task'
    epics: List[Epic] = Field(default_factory=list)
    bugs: List[Bug] = Field(default_factory=list)
    stories: List[UserStory] = Field(default_factory=list)

    def has_content(self) -> bool:
        """Check if structure has any tickets"""
        return bool(self.epics or self.bugs or self.stories)

    def count_total_items(self) -> int:
        """Count total number of tickets"""
        epic_tasks = sum(len(epic.tasks) for epic in self.epics)
        return len(self.epics) + epic_tasks + len(self.bugs) + len(self.stories)
