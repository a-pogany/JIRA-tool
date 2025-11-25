#!/bin/bash

# JIRA Ticket Generator - UI Stop Script
# Stops Flask backend and React frontend servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JIRA Ticket Generator - UI Shutdown     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Stop Flask server
if [ -f "flask.pid" ]; then
    FLASK_PID=$(cat flask.pid)
    if ps -p $FLASK_PID > /dev/null 2>&1; then
        echo -e "${BLUE}→${NC} Stopping Flask server (PID: $FLASK_PID)..."
        kill $FLASK_PID
        rm flask.pid
        echo -e "${GREEN}✓${NC} Flask server stopped"
    else
        echo -e "${BLUE}→${NC} Flask server not running"
        rm flask.pid
    fi
else
    # Try to find Flask by port
    FLASK_PID=$(lsof -ti:5010 2>/dev/null || true)
    if [ -n "$FLASK_PID" ]; then
        echo -e "${BLUE}→${NC} Stopping Flask server on port 5010 (PID: $FLASK_PID)..."
        kill $FLASK_PID
        echo -e "${GREEN}✓${NC} Flask server stopped"
    else
        echo -e "${BLUE}→${NC} No Flask server running"
    fi
fi

# Stop Vite server
if [ -f "vite.pid" ]; then
    VITE_PID=$(cat vite.pid)
    if ps -p $VITE_PID > /dev/null 2>&1; then
        echo -e "${BLUE}→${NC} Stopping Vite server (PID: $VITE_PID)..."
        kill $VITE_PID
        rm vite.pid
        echo -e "${GREEN}✓${NC} Vite server stopped"
    else
        echo -e "${BLUE}→${NC} Vite server not running"
        rm vite.pid
    fi
else
    # Try to find Vite by port
    VITE_PID=$(lsof -ti:3000 2>/dev/null || true)
    if [ -n "$VITE_PID" ]; then
        echo -e "${BLUE}→${NC} Stopping Vite server on port 3000 (PID: $VITE_PID)..."
        kill $VITE_PID
        echo -e "${GREEN}✓${NC} Vite server stopped"
    else
        echo -e "${BLUE}→${NC} No Vite server running"
    fi
fi

# Clean up log files (optional)
if [ -f "flask.log" ] || [ -f "vite.log" ]; then
    read -p "Delete log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f flask.log vite.log
        echo -e "${GREEN}✓${NC} Log files deleted"
    fi
fi

echo ""
echo -e "${GREEN}✓ Shutdown complete${NC}"
echo ""
