#!/bin/bash

# JIRA Ticket Generator - Stop Script
# Cleanup and deactivation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JIRA Ticket Generator - Cleanup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${BLUE}→${NC} Deactivating virtual environment..."
    deactivate 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Virtual environment deactivated"
else
    echo -e "${YELLOW}!${NC} Virtual environment not active"
fi

# Optional: Clean up generated markdown files older than 7 days
echo -e "${BLUE}→${NC} Checking for old markdown files..."
OLD_FILES=$(find . -maxdepth 1 -name "jira_tickets_*.md" -mtime +7 2>/dev/null | wc -l | tr -d ' ')

if [ "$OLD_FILES" -gt 0 ]; then
    echo -e "${YELLOW}!${NC} Found ${OLD_FILES} markdown file(s) older than 7 days"
    echo ""
    find . -maxdepth 1 -name "jira_tickets_*.md" -mtime +7 -exec ls -lh {} \;
    echo ""
    read -p "Do you want to delete these old files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -maxdepth 1 -name "jira_tickets_*.md" -mtime +7 -delete
        echo -e "${GREEN}✓${NC} Old markdown files deleted"
    else
        echo -e "${BLUE}→${NC} Keeping old files"
    fi
else
    echo -e "${GREEN}✓${NC} No old markdown files to clean up"
fi

# Optional: Clean up Python cache
echo -e "${BLUE}→${NC} Checking for Python cache..."
if [ -d "__pycache__" ] || [ -d "agents/__pycache__" ]; then
    read -p "Do you want to clean Python cache files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Python cache cleaned"
    else
        echo -e "${BLUE}→${NC} Keeping cache files"
    fi
else
    echo -e "${GREEN}✓${NC} No cache files to clean"
fi

echo ""
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""
echo -e "${BLUE}Tip:${NC} Run ${YELLOW}./start.sh${NC} to restart the system"
echo ""
