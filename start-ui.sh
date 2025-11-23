#!/bin/bash

# JIRA Ticket Generator - UI Start Script
# Starts both Flask backend and React frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JIRA Ticket Generator - UI Launcher     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if Python virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}!${NC} Virtual environment not active"
    echo -e "${BLUE}→${NC} Activating virtual environment..."

    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓${NC} Virtual environment activated"
    else
        echo -e "${RED}✗${NC} Virtual environment not found"
        echo -e "${BLUE}→${NC} Run: ${YELLOW}./start.sh${NC} first"
        exit 1
    fi
fi

# Install Flask dependencies if needed
echo -e "${BLUE}→${NC} Checking Flask dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}!${NC} Installing Flask..."
    pip3 install -q flask flask-cors
    echo -e "${GREEN}✓${NC} Flask installed"
else
    echo -e "${GREEN}✓${NC} Flask ready"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗${NC} Node.js not found"
    echo -e "${BLUE}→${NC} Please install Node.js from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION} found"

# Install frontend dependencies if needed
if [ ! -d "ui/node_modules" ]; then
    echo -e "${BLUE}→${NC} Installing frontend dependencies..."
    cd ui
    npm install
    cd ..
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${GREEN}✓${NC} Frontend dependencies ready"
fi

# Check if already running
FLASK_PID=$(lsof -ti:5000 2>/dev/null || true)
VITE_PID=$(lsof -ti:3000 2>/dev/null || true)

if [ -n "$FLASK_PID" ]; then
    echo -e "${YELLOW}!${NC} Flask server already running on port 5000 (PID: $FLASK_PID)"
    read -p "Kill and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $FLASK_PID
        echo -e "${GREEN}✓${NC} Stopped existing Flask server"
    fi
fi

if [ -n "$VITE_PID" ]; then
    echo -e "${YELLOW}!${NC} Vite dev server already running on port 3000 (PID: $VITE_PID)"
    read -p "Kill and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $VITE_PID
        echo -e "${GREEN}✓${NC} Stopped existing Vite server"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Starting Servers...                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Start Flask backend in background
echo -e "${BLUE}→${NC} Starting Flask backend on http://localhost:5000"
export FLASK_ENV=development
python3 app.py > flask.log 2>&1 &
FLASK_PID=$!
echo $FLASK_PID > flask.pid
sleep 2

# Check if Flask started successfully
if ps -p $FLASK_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} Flask server started (PID: $FLASK_PID)"
else
    echo -e "${RED}✗${NC} Flask server failed to start"
    echo -e "${BLUE}→${NC} Check flask.log for errors"
    exit 1
fi

# Start React frontend
echo -e "${BLUE}→${NC} Starting React frontend on http://localhost:3000"
cd ui
npm run dev > ../vite.log 2>&1 &
VITE_PID=$!
echo $VITE_PID > ../vite.pid
cd ..

sleep 2

# Check if Vite started successfully
if ps -p $VITE_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} React dev server started (PID: $VITE_PID)"
else
    echo -e "${RED}✗${NC} React dev server failed to start"
    echo -e "${BLUE}→${NC} Check vite.log for errors"
    kill $FLASK_PID
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Servers Running!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 URLs:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Flask: tail -f flask.log"
echo -e "   Vite:  tail -f vite.log"
echo ""
echo -e "${BLUE}🛑 To stop:${NC}"
echo -e "   Run: ${YELLOW}./stop-ui.sh${NC}"
echo -e "   Or:  ${YELLOW}kill $FLASK_PID $VITE_PID${NC}"
echo ""
echo -e "${GREEN}Opening browser...${NC}"
sleep 1
open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"
echo ""
