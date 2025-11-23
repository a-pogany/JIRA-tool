#!/usr/bin/env python3
"""
JIRA Ticket Generator - Main CLI

Transform unstructured text into production-ready Jira tickets
"""

import sys
import click
from pathlib import Path
from config import config
from models import IssueType
from agents.extraction_agent import ExtractionAgent


@click.group()
def cli():
    """JIRA Ticket Generator - Two-Agent AI System"""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), required=False)
@click.option('--project', '-p', help='Project key (e.g., PROJ)')
@click.option('--issue-type', '-t',
              type=click.Choice(['task', 'bug', 'story', 'epic-only'], case_sensitive=False),
              default='task',
              help='Jira issue type: task (default), bug, story, epic-only')
@click.option('--clipboard', is_flag=True, help='Read from clipboard instead of file')
@click.option('--skip-review', is_flag=True, help='Skip review agent (faster but lower quality)')
def parse(input_file, project, issue_type, clipboard, skip_review):
    """
    Parse text with two-agent system

    Examples:
        jira_gen.py parse feature.txt --issue-type task --project PROJ
        jira_gen.py parse bug.txt --issue-type bug
        jira_gen.py parse --clipboard --issue-type story
    """
    # Validate configuration
    errors = config.validate()
    if errors:
        click.echo("Configuration errors:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        click.echo("\nPlease check your .env file", err=True)
        sys.exit(1)

    # Get project key
    project_key = project or config.jira_project
    if not project_key:
        click.echo("Error: Project key required (use --project or set DEFAULT_PROJECT_KEY in .env)", err=True)
        sys.exit(1)

    # Read input text
    if clipboard:
        try:
            import pyperclip
            text = pyperclip.paste()
        except ImportError:
            click.echo("Error: pyperclip not installed. Run: pip install pyperclip", err=True)
            sys.exit(1)
    elif input_file:
        text = Path(input_file).read_text()
    else:
        click.echo("Error: Provide input file or use --clipboard", err=True)
        sys.exit(1)

    if not text.strip():
        click.echo("Error: Input text is empty", err=True)
        sys.exit(1)

    # Normalize issue type
    issue_type = issue_type.lower()  # type: ignore

    click.echo(f"\n🚀 JIRA Ticket Generator")
    click.echo(f"   Issue Type: {issue_type}")
    click.echo(f"   Project: {project_key}")
    click.echo(f"   Input Length: {len(text)} characters")

    # Get LLM client if configured
    llm_client = None
    if config.has_llm_configured():
        try:
            llm_client = config.get_llm_client()
            click.echo(f"   LLM: {config.llm_provider} ({config.llm_model})")
        except Exception as e:
            click.echo(f"   Warning: LLM not available ({e})", err=True)
            click.echo("   Using fallback mode", err=True)
    else:
        click.echo("   LLM: Not configured (using fallback mode)")

    # Agent 1: Extract structure
    click.echo("\n📝 Agent 1: Extracting structure...")
    extraction_agent = ExtractionAgent(llm_client, issue_type=issue_type)  # type: ignore
    structure = extraction_agent.extract(text, project_key)

    if not structure.has_content():
        click.echo("Error: No tickets extracted from input", err=True)
        sys.exit(1)

    # Display results
    click.echo(f"\n✅ Extraction complete!")
    click.echo(f"   Total items: {structure.count_total_items()}")

    if structure.epics:
        click.echo(f"   Epics: {len(structure.epics)}")
        total_tasks = sum(len(epic.tasks) for epic in structure.epics)
        click.echo(f"   Tasks: {total_tasks}")

    if structure.bugs:
        click.echo(f"   Bugs: {len(structure.bugs)}")

    if structure.stories:
        click.echo(f"   Stories: {len(structure.stories)}")

    # TODO: Agent 2 review (Phase 2)
    if not skip_review:
        click.echo("\n⏭️  Agent 2 review not yet implemented (coming in Phase 2)")

    # TODO: Save to markdown (Phase 2)
    click.echo("\n📄 Markdown generation not yet implemented (coming in Phase 2)")
    click.echo("   For now, showing extracted structure:\n")

    # Display extracted content
    if structure.epics:
        for i, epic in enumerate(structure.epics, 1):
            click.echo(f"\n{'='*60}")
            click.echo(f"Epic {i}: {epic.title}")
            click.echo(f"{'='*60}")
            click.echo(f"Priority: {epic.priority}")
            if epic.business_value:
                click.echo(f"Business Value: {epic.business_value}")
            click.echo(f"\nDescription:\n{epic.description}")

            if epic.tasks:
                click.echo(f"\nTasks ({len(epic.tasks)}):")
                for j, task in enumerate(epic.tasks, 1):
                    click.echo(f"\n  Task {j}: {task.title}")
                    click.echo(f"  Priority: {task.priority}")
                    if task.acceptance_criteria:
                        click.echo(f"  Acceptance Criteria ({len(task.acceptance_criteria)}):")
                        for ac in task.acceptance_criteria:
                            click.echo(f"    - {ac}")

    if structure.bugs:
        for i, bug in enumerate(structure.bugs, 1):
            click.echo(f"\n{'='*60}")
            click.echo(f"Bug {i}: {bug.summary}")
            click.echo(f"{'='*60}")
            click.echo(f"Severity: {bug.severity} | Priority: {bug.priority}")
            click.echo(f"\nDescription:\n{bug.description}")
            click.echo(f"\nReproduction Steps:")
            for j, step in enumerate(bug.reproduction_steps, 1):
                click.echo(f"  {j}. {step}")

    if structure.stories:
        for i, story in enumerate(structure.stories, 1):
            click.echo(f"\n{'='*60}")
            click.echo(f"Story {i}: {story.title}")
            click.echo(f"{'='*60}")
            click.echo(f"As a: {story.as_a}")
            click.echo(f"I want to: {story.i_want_to}")
            click.echo(f"So that: {story.so_that}")
            click.echo(f"\nAcceptance Criteria:")
            for ac in story.acceptance_criteria:
                click.echo(f"  - {ac}")


@cli.command()
def validate():
    """Validate configuration"""
    errors = config.validate()

    if errors:
        click.echo("❌ Configuration validation failed:\n", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        click.echo("\nPlease check your .env file", err=True)
        sys.exit(1)
    else:
        click.echo("✅ Configuration is valid")
        click.echo(f"\n   Jira URL: {config.jira_url}")
        click.echo(f"   Jira Email: {config.jira_email}")
        click.echo(f"   Project Key: {config.jira_project or '(not set)'}")
        click.echo(f"   LLM Provider: {config.llm_provider}")
        click.echo(f"   LLM Model: {config.llm_model}")


if __name__ == '__main__':
    cli()
