# JIRA Ticket Generator - Web UI

Modern, clean web interface for the JIRA Ticket Generator with React frontend and Flask backend.

## Features

✅ **File Upload** - Upload meeting transcripts, notes, or requirements (.txt, .md, .doc, .docx)
✅ **Text Input** - Type or paste text directly into the web interface
✅ **Live Preview** - Real-time preview of generated tickets in markdown format
✅ **Markdown Editor** - Edit generated tickets before uploading to Jira
✅ **File Management** - Browse, view, edit, and delete previously generated tickets
✅ **Issue Type Selection** - Choose from Tasks/Epics, Bug Reports, User Stories, Epic-only
✅ **Review Agent Integration** - Optional AI review with quality feedback
✅ **Jira Upload** - Upload tickets directly to Jira (when configured)

---

## Quick Start

### 1. Install Dependencies

**Backend (Python)**:
```bash
# From project root
./start.sh  # Sets up Python environment and dependencies
```

**Frontend (Node.js)**:
```bash
# Install Node.js from https://nodejs.org/ (v18+ recommended)
# Dependencies will be installed automatically by start-ui.sh
```

### 2. Start the UI

```bash
./start-ui.sh
```

This will:
- Start Flask backend on http://localhost:5000
- Start React frontend on http://localhost:3000
- Open your browser automatically

### 3. Use the Web Interface

1. **Upload a file** or **type/paste text** into the text area
2. **Select issue type** (Tasks, Bugs, Stories, Epic-only)
3. **Enter project key** (e.g., PROJ, MYAPP)
4. **Click "Generate Tickets"**
5. **Review the results** - View stats, review feedback, and generated markdown
6. **Edit if needed** - Click "Edit" to modify the markdown
7. **Upload to Jira** - Click "Upload to Jira" when ready

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              React Frontend (Port 3000)         │
│  • Vite dev server                              │
│  • Tailwind CSS for styling                    │
│  • Axios for API calls                          │
│  • React Markdown for preview                  │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/API
┌──────────────────▼──────────────────────────────┐
│              Flask Backend (Port 5000)          │
│  • REST API endpoints                           │
│  • Integration with existing Python code       │
│  • File management (upload, list, edit)        │
│  • Jira API integration                         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Existing Python Components              │
│  • ExtractionAgent (Agent 1)                    │
│  • ReviewAgent (Agent 2)                        │
│  • Markdown utilities                           │
│  • Jira client                                  │
└─────────────────────────────────────────────────┘
```

---

## API Endpoints

### Health & Config
- `GET /api/health` - Health check and status
- `GET /api/config` - Get current configuration
- `GET /api/validate` - Validate configuration

### Ticket Generation
- `POST /api/parse` - Parse text and generate tickets
  - Body: `{ text, project_key, issue_type, skip_review }`
  - File upload supported via multipart/form-data

### Markdown Management
- `GET /api/markdown/list` - List all markdown files
- `GET /api/markdown/<filename>` - Get markdown content
- `PUT /api/markdown/<filename>` - Update markdown content
- `DELETE /api/markdown/<filename>` - Delete markdown file

### Jira Integration
- `POST /api/upload-to-jira` - Upload markdown to Jira
  - Body: `{ filename }`

---

## Development

### Frontend Development

```bash
cd ui
npm run dev    # Start dev server with hot reload
npm run build  # Build for production
npm run preview  # Preview production build
```

### Backend Development

```bash
export FLASK_ENV=development
python3 app.py  # Start Flask with debug mode
```

### Project Structure

```
ui/
├── public/           # Static assets
├── src/
│   ├── components/   # React components
│   │   ├── Header.jsx
│   │   ├── InputPanel.jsx
│   │   ├── ResultsPanel.jsx
│   │   ├── MarkdownEditor.jsx
│   │   └── FilesPanel.jsx
│   ├── App.jsx       # Main app component
│   ├── main.jsx      # Entry point
│   └── index.css     # Global styles
├── package.json      # Dependencies
├── vite.config.js    # Vite configuration
└── tailwind.config.js  # Tailwind configuration
```

---

## Features in Detail

### File Upload
- Supports .txt, .md, .doc, .docx files
- Drag and drop interface
- Automatic file content loading into text area
- File size limit: 16MB

### Text Input
- Large expandable text area
- Character count indicator
- Automatic content preservation
- Paste support with formatting cleanup

### Issue Type Selection
- **Tasks/Epics** (📋) - Feature development with nested tasks
- **Bug Reports** (🐛) - Detailed bug descriptions with reproduction steps
- **User Stories** (📖) - Agile format with acceptance criteria
- **Epic-only** (🎯) - High-level planning without detailed tasks

### Review Agent (Agent 2)
- Optional AI-powered quality review
- Identifies gaps, ambiguities, missing tasks
- Provides clarifying questions
- Offers suggestions for improvement
- Production readiness assessment
- Toggle on/off for faster generation

### Markdown Editor
- Syntax-highlighted editing
- Line and character count
- Save/reset functionality
- Unsaved changes indicator
- Full-screen editing capability

### File Management
- List all generated markdown files
- Sorted by newest first (newest at top)
- File size and last modified display
- Click to view/edit
- Delete with confirmation
- Automatic refresh

---

## Configuration

The UI uses the same `.env` configuration as the CLI:

```bash
# LLM Provider (required for Agent 1 and 2)
LLM_PROVIDER=openai              # or 'anthropic'
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=gpt-4-turbo

# Jira Configuration (optional for generation, required for upload)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
DEFAULT_PROJECT_KEY=PROJ
```

---

## Troubleshooting

### Port Already in Use

**Error**: `Port 5000 (or 3000) is already in use`

**Solution**:
```bash
# Kill existing processes
./stop-ui.sh

# Or manually
lsof -ti:5000 | xargs kill
lsof -ti:3000 | xargs kill
```

### Flask Import Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate venv and install
source venv/bin/activate
pip install flask flask-cors
```

### Node.js Not Found

**Error**: `node: command not found`

**Solution**:
```bash
# Install Node.js from https://nodejs.org/
# Or using homebrew:
brew install node
```

### Frontend Build Fails

**Error**: `npm run build` fails

**Solution**:
```bash
cd ui
rm -rf node_modules package-lock.json
npm install
npm run build
```

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: Flask-CORS is already configured. If issues persist:
```python
# In app.py, ensure CORS is enabled:
from flask_cors import CORS
CORS(app)
```

---

## Production Deployment

### Build Frontend

```bash
cd ui
npm run build
```

This creates an optimized production build in `ui/build/`.

### Run Production Server

```bash
export FLASK_ENV=production
export PORT=8080
python3 app.py
```

Flask will serve the React build from `ui/build/` automatically.

### Environment Variables for Production

```bash
# Production settings
FLASK_ENV=production
PORT=8080

# LLM and Jira (same as development)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
JIRA_URL=https://...
JIRA_EMAIL=...
JIRA_API_TOKEN=...
```

---

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## Performance

**Typical Response Times**:
- File upload: < 1s
- Ticket generation (with LLM): 5-15s
- Ticket generation (without review): 5-10s
- Markdown save: < 500ms
- File list: < 200ms

**Optimizations**:
- React lazy loading for components
- Tailwind CSS purging for small bundle size
- Vite for fast dev server and HMR
- API response caching where appropriate

---

## Tips & Best Practices

### For Best Results

1. **Clear Input**: Provide structured, clear descriptions
2. **Include Details**: Mention security, performance, error handling requirements
3. **Use Review Agent**: Let Agent 2 validate quality (adds 10-15s)
4. **Edit Before Upload**: Always review and edit generated markdown
5. **Use Project Keys**: Set meaningful project keys (MYAPP, PROJ, etc.)

### Example Inputs

**Good Input**:
```
Build user authentication system. Users should login with email and password.
Add password reset via email. Security is critical - implement rate limiting
and use bcrypt for password hashing. Performance should be fast (<200ms).
```

**Why it works**:
- Clear feature description
- Mentions security explicitly
- Includes performance requirements
- Specific technologies mentioned

---

## Screenshots

### Input Panel
Clean, simple interface for file upload or text input with issue type selection.

### Results Panel
Generated tickets with stats, review feedback, and markdown preview.

### Markdown Editor
Full-featured editor with syntax highlighting and save/reset controls.

### Files Panel
Browse and manage all generated markdown files with quick access.

---

## License

MIT License - Same as parent project

---

## Support

**Issues**: https://github.com/a-pogany/JIRA-tool/issues
**Documentation**: See main [README.md](../README.md)
**CLI Reference**: Use `python3 jira_gen.py --help`

---

**Built with React + Flask • Styled with Tailwind CSS • Powered by AI** 🚀
