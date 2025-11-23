#!/bin/bash

# JIRA Ticket Generator - Start Script
# Quick setup and validation before running the tool

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JIRA Ticket Generator - Startup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${BLUE}→${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}!${NC} Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo -e "${BLUE}→${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Check and install dependencies
echo -e "${BLUE}→${NC} Checking dependencies..."
if [ -f "requirements.txt" ]; then
    # Check if dependencies are already installed
    pip3 list --format=freeze > /tmp/installed_packages.txt
    MISSING_DEPS=0

    while IFS= read -r package; do
        # Extract package name (before >=)
        pkg_name=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1)
        if ! grep -q "^${pkg_name}==" /tmp/installed_packages.txt; then
            MISSING_DEPS=1
            break
        fi
    done < requirements.txt

    if [ $MISSING_DEPS -eq 1 ]; then
        echo -e "${YELLOW}!${NC} Installing missing dependencies..."
        pip3 install -q -r requirements.txt
        echo -e "${GREEN}✓${NC} Dependencies installed"
    else
        echo -e "${GREEN}✓${NC} All dependencies already installed"
    fi

    rm /tmp/installed_packages.txt
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    exit 1
fi

# Check .env file
echo -e "${BLUE}→${NC} Checking configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}!${NC} .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env file created"
        echo -e "${YELLOW}!${NC} Please edit .env file with your API keys"
        echo ""
        echo -e "${BLUE}Required settings:${NC}"
        echo "  - LLM_PROVIDER (openai or anthropic)"
        echo "  - OPENAI_API_KEY or ANTHROPIC_API_KEY"
        echo "  - JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN (optional for Phase 1)"
        echo ""
        echo -e "${YELLOW}Run './start.sh' again after configuring .env${NC}"
        exit 0
    else
        echo -e "${RED}✗${NC} .env.example not found"
        exit 1
    fi
fi

# Validate configuration
echo -e "${BLUE}→${NC} Validating configuration..."
if python3 jira_gen.py validate > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Configuration is valid"
else
    echo -e "${YELLOW}!${NC} Configuration validation failed"
    echo -e "${YELLOW}Run: python3 jira_gen.py validate${NC} for details"
    echo ""
fi

# Display usage information
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Ready to use! Here's how:               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Usage Examples:${NC}"
echo ""
echo -e "  ${YELLOW}1. Generate tickets from file:${NC}"
echo "     python3 jira_gen.py parse input.txt --project PROJ"
echo ""
echo -e "  ${YELLOW}2. Generate bug report:${NC}"
echo "     python3 jira_gen.py parse bug.txt --issue-type bug --project PROJ"
echo ""
echo -e "  ${YELLOW}3. From clipboard:${NC}"
echo "     python3 jira_gen.py parse --clipboard --issue-type story --project PROJ"
echo ""
echo -e "  ${YELLOW}4. List markdown files:${NC}"
echo "     python3 jira_gen.py upload --list"
echo ""
echo -e "  ${YELLOW}5. Validate configuration:${NC}"
echo "     python3 jira_gen.py validate"
echo ""
echo -e "${BLUE}Tip:${NC} Use ${YELLOW}./status.sh${NC} to check system health anytime"
echo ""
echo -e "${GREEN}Happy ticket generating! 🎉${NC}"
echo ""
