#!/bin/bash

# JIRA Ticket Generator - Status Script
# Check system health and configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JIRA Ticket Generator - System Status   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Overall status tracking
ALL_GOOD=true

# 1. Python Installation
echo -e "${BLUE}[1/7]${NC} Python Installation"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "      ${GREEN}✓${NC} Python ${PYTHON_VERSION} installed"
else
    echo -e "      ${RED}✗${NC} Python 3 not found"
    ALL_GOOD=false
fi

# 2. Virtual Environment
echo -e "${BLUE}[2/7]${NC} Virtual Environment"
if [ -d "venv" ]; then
    echo -e "      ${GREEN}✓${NC} Virtual environment exists"
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "      ${GREEN}✓${NC} Virtual environment active"
    else
        echo -e "      ${YELLOW}!${NC} Virtual environment not activated"
        echo -e "         ${BLUE}→${NC} Run: ${YELLOW}source venv/bin/activate${NC}"
    fi
else
    echo -e "      ${RED}✗${NC} Virtual environment not found"
    echo -e "         ${BLUE}→${NC} Run: ${YELLOW}./start.sh${NC} to create it"
    ALL_GOOD=false
fi

# 3. Dependencies
echo -e "${BLUE}[3/7]${NC} Dependencies"
if [ -f "requirements.txt" ]; then
    # Activate venv if exists but not active
    if [ -d "venv" ] && [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate 2>/dev/null
    fi

    # Check key dependencies
    MISSING_DEPS=()
    for pkg in "click" "pydantic" "openai" "anthropic"; do
        if ! python3 -c "import $pkg" 2>/dev/null; then
            MISSING_DEPS+=("$pkg")
        fi
    done

    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        echo -e "      ${GREEN}✓${NC} All dependencies installed"
    else
        echo -e "      ${RED}✗${NC} Missing: ${MISSING_DEPS[*]}"
        echo -e "         ${BLUE}→${NC} Run: ${YELLOW}pip3 install -r requirements.txt${NC}"
        ALL_GOOD=false
    fi
else
    echo -e "      ${RED}✗${NC} requirements.txt not found"
    ALL_GOOD=false
fi

# 4. Configuration File
echo -e "${BLUE}[4/7]${NC} Configuration File"
if [ -f ".env" ]; then
    echo -e "      ${GREEN}✓${NC} .env file exists"

    # Check key configuration values
    if grep -q "^LLM_PROVIDER=" .env; then
        LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        echo -e "      ${GREEN}✓${NC} LLM Provider: ${LLM_PROVIDER}"
    else
        echo -e "      ${YELLOW}!${NC} LLM_PROVIDER not set"
    fi

    # Check API key based on provider
    if [ "$LLM_PROVIDER" = "openai" ]; then
        if grep -q "^OPENAI_API_KEY=sk-" .env; then
            echo -e "      ${GREEN}✓${NC} OpenAI API key configured"
        else
            echo -e "      ${YELLOW}!${NC} OpenAI API key not set or invalid"
        fi
    elif [ "$LLM_PROVIDER" = "anthropic" ]; then
        if grep -q "^ANTHROPIC_API_KEY=sk-ant-" .env; then
            echo -e "      ${GREEN}✓${NC} Anthropic API key configured"
        else
            echo -e "      ${YELLOW}!${NC} Anthropic API key not set or invalid"
        fi
    fi
else
    echo -e "      ${RED}✗${NC} .env file not found"
    echo -e "         ${BLUE}→${NC} Run: ${YELLOW}./start.sh${NC} to create from template"
    ALL_GOOD=false
fi

# 5. Configuration Validation
echo -e "${BLUE}[5/7]${NC} Configuration Validation"
if [ -f "jira_gen.py" ] && [ -f ".env" ]; then
    if python3 jira_gen.py validate > /tmp/validate_output.txt 2>&1; then
        echo -e "      ${GREEN}✓${NC} Configuration valid"
        # Show project key if available
        if grep -q "Project Key:" /tmp/validate_output.txt; then
            PROJECT=$(grep "Project Key:" /tmp/validate_output.txt | awk -F': ' '{print $2}')
            if [ "$PROJECT" != "(not set)" ]; then
                echo -e "      ${GREEN}✓${NC} Project: ${PROJECT}"
            fi
        fi
    else
        echo -e "      ${RED}✗${NC} Configuration validation failed"
        echo -e "         ${BLUE}→${NC} Run: ${YELLOW}python3 jira_gen.py validate${NC} for details"
        ALL_GOOD=false
    fi
    rm -f /tmp/validate_output.txt
else
    echo -e "      ${YELLOW}!${NC} Cannot validate (missing files)"
fi

# 6. Recent Activity
echo -e "${BLUE}[6/7]${NC} Recent Activity"
RECENT_MD=$(find . -maxdepth 1 -name "jira_tickets_*.md" -mtime -1 2>/dev/null | wc -l | tr -d ' ')
TOTAL_MD=$(find . -maxdepth 1 -name "jira_tickets_*.md" 2>/dev/null | wc -l | tr -d ' ')

if [ "$TOTAL_MD" -gt 0 ]; then
    echo -e "      ${GREEN}✓${NC} ${TOTAL_MD} markdown file(s) total"
    if [ "$RECENT_MD" -gt 0 ]; then
        echo -e "      ${GREEN}✓${NC} ${RECENT_MD} file(s) created in last 24h"
    fi
else
    echo -e "      ${BLUE}→${NC} No markdown files yet"
fi

# 7. Disk Space
echo -e "${BLUE}[7/7]${NC} Disk Space"
PROJECT_SIZE=$(du -sh . 2>/dev/null | awk '{print $1}')
echo -e "      ${GREEN}✓${NC} Project size: ${PROJECT_SIZE}"

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}║   ✓ System Status: HEALTHY                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    echo ""
    echo -e "${BLUE}Quick Actions:${NC}"
    echo -e "  • Generate tickets: ${YELLOW}python3 jira_gen.py parse input.txt --project PROJ${NC}"
    echo -e "  • List files:       ${YELLOW}python3 jira_gen.py upload --list${NC}"
else
    echo -e "${YELLOW}║   ! System Status: NEEDS ATTENTION         ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Some issues detected. See above for details.${NC}"
    echo ""
    echo -e "${BLUE}Suggested Actions:${NC}"
    echo -e "  • Run setup:       ${YELLOW}./start.sh${NC}"
    echo -e "  • Validate config: ${YELLOW}python3 jira_gen.py validate${NC}"
fi
echo ""
