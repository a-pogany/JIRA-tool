# Phase 2 UI Design Specification

## Overview

Simple, clean web interface for JIRA Ticket Generator with focus on usability and efficiency.

**Technology Stack:**
- Frontend: React + Tailwind CSS (modern, clean UI)
- Backend: Flask/FastAPI (Python, integrates with existing codebase)
- State Management: React Context API (simple, no overhead)
- File Storage: Local filesystem (markdown files)

---

## User Flows

### Flow 1: Quick Ticket Generation
```
1. User arrives at homepage
2. Pastes text OR uploads file
3. Selects issue type (task/bug/story/epic-only)
4. Clicks "Generate Tickets"
5. Views extracted tickets
6. (Optional) Edits markdown
7. Uploads to Jira
```

### Flow 2: Review & Edit Workflow
```
1. User generates tickets
2. Reviews extracted structure
3. Clicks "Edit Markdown"
4. Makes changes in editor
5. Saves changes
6. Uploads to Jira
```

### Flow 3: Browse Previous Sessions
```
1. User clicks "Previous Sessions"
2. Views list of generated markdown files
3. Selects a file
4. Reviews/edits content
5. Uploads to Jira
```

---

## UI Layout

### Main Page (Single-Page Application)

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 JIRA Ticket Generator                          [⚙️ Config] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  📝 Input                                                │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  [📎 Upload File]  or  [Type/Paste Text Below]          │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │                                                     │ │ │
│  │  │  Type or paste your meeting notes,                │ │ │
│  │  │  bug description, or requirements here...          │ │ │
│  │  │                                                     │ │ │
│  │  │  [Text area - auto-expands]                        │ │ │
│  │  │                                                     │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  │                                                          │ │
│  │  Issue Type:  [▼ Tasks/Epics ▼]                         │ │
│  │               • Tasks/Epics  • Bug Reports              │ │
│  │               • User Stories • Epic-only                │ │
│  │                                                          │ │
│  │  Project Key: [PROJ______]                              │ │
│  │                                                          │ │
│  │              [🚀 Generate Tickets]                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ✨ Generated Tickets                   [📝 Edit] [⬆️ Upload] │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  Epic: User Authentication System                        │ │
│  │  ├─ Task 1: Implement login endpoint                    │ │
│  │  │  ├─ ✓ POST /api/auth/login returns JWT              │ │
│  │  │  ├─ ✓ Rate limiting 5/min per IP                    │ │
│  │  │  ├─ ✓ Password validation with bcrypt               │ │
│  │  │  └─ ✓ Error: 401 "Invalid credentials"              │ │
│  │  └─ Task 2: Password reset functionality                │ │
│  │     └─ [Expandable...]                                  │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  [📂 Previous Sessions (3)]                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Designs

### 1. Input Section

**Features:**
- Drag & drop file upload
- File type: .txt, .md, .docx (transcript files)
- Text area with auto-expand
- Character count display
- Clear/Reset button

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  📝 Input                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Upload File                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │      📎 Drag & drop file here                           │ │
│  │      or [Browse Files]                                  │ │
│  │                                                         │ │
│  │      Accepted: .txt, .md, .docx                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ─────────────────── OR ────────────────────                │
│                                                              │
│  Type/Paste Text                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Enter your meeting notes, requirements, or bug          │ │
│  │ description here...                                     │ │
│  │                                                         │ │
│  │ Example:                                                │ │
│  │ "Build user authentication system. Users should login  │ │
│  │  with email and password..."                            │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│  Characters: 245 / 10,000                      [Clear Text] │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2. Configuration Section

**Features:**
- Issue type selector (visual cards)
- Project key input
- Optional: Agent 2 enable/disable
- Optional: LLM model selection

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Configuration                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Issue Type                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ 📋 Task │  │ 🐛 Bug  │  │ 📖 Story│  │ 🎯 Epic │       │
│  │ /Epics  │  │ Reports │  │         │  │  Only   │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│    [Selected]                                                │
│                                                              │
│  Project Key                                                 │
│  [PROJ__________________]                                    │
│                                                              │
│  ☑ Enable Review Agent (Agent 2)                            │
│                                                              │
│              [🚀 Generate Tickets]                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3. Results Display

**Features:**
- Collapsible epic/task tree view
- Acceptance criteria checklist display
- Syntax highlighting for markdown
- Export to markdown button
- Copy to clipboard

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✨ Generated Tickets          [📝 Edit] [⬆️ Jira] [📋 Copy] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ Epic: User Authentication System                   [High]│
│     Business Value: Enables secure user account mgmt        │
│                                                              │
│     ▼ Task 1: Implement login endpoint with JWT      [High]│
│        Effort: Medium                                        │
│                                                              │
│        Acceptance Criteria:                                  │
│        ☑ Functional: POST /api/auth/login returns tokens   │
│        ☑ Security: Rate limiting 5 attempts/min per IP     │
│        ☑ Security: Password validation with bcrypt         │
│        ☑ Error: 401 with "Invalid email or password"       │
│        ☑ Performance: Login completes < 200ms              │
│        ☑ Testing: Unit tests for token generation          │
│        ☑ Edge: Handles SQL injection safely                │
│                                                              │
│        Technical Notes:                                      │
│        • Use jsonwebtoken library                           │
│        • Access token: 15min expiry                         │
│        • Store in httpOnly cookies                          │
│        • Database: users table (email, password_hash)       │
│                                                              │
│     ▶ Task 2: Password reset functionality            [High]│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4. Markdown Editor Modal

**Features:**
- Full-screen markdown editor
- Live preview (split-pane)
- Syntax highlighting
- Save/Cancel actions
- Format toolbar

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  📝 Edit Markdown                           [Save] [Cancel]  │
├──────────────────────────┬──────────────────────────────────┤
│ # Epic: User Auth System │  Epic: User Auth System          │
│                          │                                  │
│ **Business Value:**      │  Business Value:                 │
│ Enables secure user...   │  Enables secure user...          │
│                          │                                  │
│ ## Task 1: Login         │  Task 1: Login                   │
│                          │                                  │
│ **Acceptance Criteria:** │  Acceptance Criteria:            │
│ - Functional: POST...    │  • Functional: POST...           │
│ - Security: Rate...      │  • Security: Rate...             │
│                          │                                  │
│ [Markdown Editor]        │  [Live Preview]                  │
│                          │                                  │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

### 5. Jira Upload Modal

**Features:**
- Project key confirmation
- Epic-Task linking preview
- Upload progress
- Success/Error messages
- Dry-run option

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⬆️ Upload to Jira                                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Project: PROJ                                    [Change]   │
│                                                              │
│  Tickets to create:                                          │
│  ✓ 1 Epic: User Authentication System                       │
│  ✓ 2 Tasks under epic                                       │
│                                                              │
│  ☐ Dry-run (validate without creating)                      │
│                                                              │
│  ⚠️ This will create 3 tickets in Jira                       │
│                                                              │
│                    [Cancel]  [Upload to Jira]                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Progress State:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⬆️ Uploading to Jira...                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ Created Epic: AUTH-101                                   │
│  🔄 Creating Task 1...                                       │
│  ⏳ Pending Task 2...                                        │
│                                                              │
│  ████████████░░░░░░░░░  66%                                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6. Previous Sessions Sidebar

**Features:**
- List recent markdown files
- Timestamp display
- Quick preview
- Load/Delete actions

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  📂 Previous Sessions                              [Refresh] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ jira_tickets_20251123_143022.md            [Load] [X]│   │
│  │ 📋 1 Epic, 2 Tasks                                   │   │
│  │ 🕐 2 hours ago                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ jira_tickets_20251123_095510.md            [Load] [X]│   │
│  │ 🐛 3 Bug Reports                                     │   │
│  │ 🕐 5 hours ago                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ jira_tickets_20251122_161245.md            [Load] [X]│   │
│  │ 📖 4 User Stories                                    │   │
│  │ 🕐 Yesterday                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [View All (12 files)]                                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7. Settings Modal

**Features:**
- Jira configuration
- LLM provider selection
- API key management
- Default project key

**Mockup:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                    [Save] [Cancel]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Jira Configuration                                          │
│  ├─ Jira URL: [https://your-domain.atlassian.net____]      │
│  ├─ Email: [your-email@example.com_______________]          │
│  └─ API Token: [••••••••••••••••••••••]    [Reveal]         │
│                                                              │
│  LLM Configuration                                           │
│  ├─ Provider: (•) OpenAI  ( ) Anthropic                     │
│  ├─ API Key: [••••••••••••••••••••••]     [Reveal]          │
│  └─ Model: [▼ gpt-4-turbo ▼]                                │
│                                                              │
│  Defaults                                                    │
│  └─ Project Key: [PROJ__________________]                   │
│                                                              │
│              [Test Connection]  [Save Settings]              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Color Scheme & Design System

### Colors (Tailwind-based)

```css
Primary: #3B82F6 (blue-500) - Actions, buttons
Success: #10B981 (green-500) - Completed, success states
Warning: #F59E0B (amber-500) - Warnings, important info
Error: #EF4444 (red-500) - Errors, destructive actions
Gray: #6B7280 (gray-500) - Text, borders
Background: #F9FAFB (gray-50) - Page background
Surface: #FFFFFF - Cards, modals
```

### Typography

```
Headings: Inter/SF Pro (system font)
Body: System font stack
Code: JetBrains Mono / Fira Code
```

### Components

```
Buttons:
- Primary: Blue background, white text, rounded-lg
- Secondary: White background, blue border, blue text
- Danger: Red background, white text

Cards:
- White background
- Shadow-sm
- Rounded-lg borders
- Hover: shadow-md transition

Inputs:
- Border-gray-300
- Focus: border-blue-500, ring-blue-500
- Rounded-md
```

---

## Technical Architecture

### Frontend Structure

```
web-ui/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── InputSection.jsx
│   │   ├── ConfigSection.jsx
│   │   ├── ResultsDisplay.jsx
│   │   ├── MarkdownEditor.jsx
│   │   ├── JiraUploadModal.jsx
│   │   ├── PreviousSessions.jsx
│   │   └── SettingsModal.jsx
│   ├── context/
│   │   └── AppContext.jsx
│   ├── services/
│   │   ├── api.js
│   │   └── markdown.js
│   ├── App.jsx
│   └── index.js
└── package.json
```

### Backend API Endpoints

```python
# Flask/FastAPI Backend

POST /api/parse
  Body: {
    text: string,
    issueType: "task" | "bug" | "story" | "epic-only",
    projectKey: string,
    enableReview: boolean
  }
  Response: {
    structure: TicketStructure,
    markdown: string,
    filename: string
  }

GET /api/sessions
  Response: {
    files: [
      {
        filename: string,
        timestamp: datetime,
        summary: { epics: number, tasks: number, bugs: number }
      }
    ]
  }

GET /api/sessions/:filename
  Response: {
    content: string,
    structure: TicketStructure
  }

POST /api/jira/upload
  Body: {
    markdown: string,
    projectKey: string,
    dryRun: boolean
  }
  Response: {
    success: boolean,
    tickets: [
      { key: string, type: string, title: string, url: string }
    ]
  }

POST /api/config/validate
  Body: { jiraUrl, jiraEmail, jiraToken, llmProvider, llmApiKey }
  Response: { valid: boolean, errors: [] }

POST /api/config/save
  Body: { ... config settings }
  Response: { success: boolean }
```

---

## Responsive Design

### Desktop (1024px+)
- Single page layout
- Side-by-side markdown editor
- Full feature set visible

### Tablet (768px - 1023px)
- Stacked layout
- Collapsible sections
- Modal editor (full-screen)

### Mobile (< 768px)
- Single column
- Bottom navigation
- Simplified interface
- Touch-optimized buttons

---

## User Experience Enhancements

### 1. Auto-save
- Save input text to localStorage
- Restore on page reload
- Prevent data loss

### 2. Keyboard Shortcuts
- `Ctrl+Enter`: Generate tickets
- `Ctrl+E`: Open markdown editor
- `Ctrl+U`: Upload to Jira
- `Ctrl+,`: Open settings

### 3. Progress Indicators
- Loading spinner during generation
- Progress bar for Jira upload
- Toast notifications for success/error

### 4. Helpful Hints
- Placeholder examples in text area
- Tooltips on hover
- "Getting Started" tutorial (first visit)

### 5. Error Handling
- Clear error messages
- Suggested fixes
- Validation before actions

---

## Implementation Phases

### Phase 2.1: Core UI (Week 1)
- [ ] Input section (file upload + text area)
- [ ] Config section (issue type, project key)
- [ ] Generate tickets functionality
- [ ] Results display (basic)

### Phase 2.2: Editor & Sessions (Week 2)
- [ ] Markdown editor modal
- [ ] Previous sessions sidebar
- [ ] Load/save markdown files

### Phase 2.3: Jira Integration (Week 3)
- [ ] Jira upload modal
- [ ] Upload progress tracking
- [ ] Settings modal
- [ ] Configuration validation

### Phase 2.4: Polish & UX (Week 4)
- [ ] Responsive design
- [ ] Keyboard shortcuts
- [ ] Auto-save
- [ ] Tutorial/onboarding
- [ ] Error handling improvements

---

## Technology Choices Rationale

**React:**
- Component-based architecture
- Rich ecosystem
- Easy state management

**Tailwind CSS:**
- Rapid UI development
- Consistent design system
- Small bundle size

**Flask/FastAPI:**
- Python integration (existing codebase)
- Simple RESTful API
- Easy deployment

**No Database (Phase 2):**
- Markdown files on filesystem
- Simple, portable
- Easy backup/version control

---

## Next Steps

1. ✅ Approve UI design
2. ⏭️ Set up React project
3. ⏭️ Implement core components
4. ⏭️ Build Flask API endpoints
5. ⏭️ Integrate with Phase 1 codebase
6. ⏭️ Testing & refinement

---

**Design Status**: ✅ Ready for implementation
**Estimated Effort**: 3-4 weeks for full Phase 2
