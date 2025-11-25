# Troubleshooting Guide

## Port Configuration

### Current Setup
The application now uses **port 5010** for the Flask backend to avoid conflicts with macOS Control Center.

- **Frontend**: http://localhost:3000 (Vite dev server)
- **Backend**: http://localhost:5010 (Flask API)

### Changed from Port 5000
macOS Control Center uses port 5000 for AirPlay Receiver by default. To avoid this conflict, the application has been configured to use port 5010 instead.

### To Change the Port
If you need to use a different port:

1. **Edit `app.py`:**
```python
port = int(os.getenv('PORT', 5010))  # Change 5010 to your port
```

2. **Edit `ui/vite.config.js`:**
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5010',  // Change 5010 to match app.py
    changeOrigin: true
  }
}
```

3. **Edit `start-ui.sh`:** Update port references in the startup script

## Flask Import Error

### Problem
`ModuleNotFoundError: No module named 'flask'`

### Solution
The project uses `uv` for package management. Install Flask:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install Flask with uv
uv pip install flask flask-cors

# Or if uv is not available
python -m pip install flask flask-cors
```

## Virtual Environment Issues

### Multiple Virtual Environments
If you see both `.venv` and `venv` directories, use `.venv` (standard):

```bash
# Remove the old venv
rm -rf venv

# Always use .venv
source .venv/bin/activate
```

## Node.js Dependency Issues

### Problem
Frontend dependencies not installing or outdated

### Solution
```bash
cd ui
rm -rf node_modules package-lock.json
npm install
cd ..
```

## Server Start Issues

### Check Logs
```bash
# View Flask logs
tail -f flask.log

# View Vite logs
tail -f vite.log
```

### Stop All Servers
```bash
# Use the stop script
./stop-ui.sh

# Or manually kill processes
kill $(cat flask.pid vite.pid 2>/dev/null)

# Or by port
kill $(lsof -ti:5000)
kill $(lsof -ti:3000)
```

## Common Error Messages

### "Address already in use"
- Port is occupied by another process
- Check with `lsof -i :5000` or `lsof -i :3000`
- Kill the process or use a different port

### "Cannot find module"
- Dependencies not installed
- Run `./start.sh` to install all dependencies

### "Permission denied"
- Script not executable
- Run `chmod +x start-ui.sh stop-ui.sh`
