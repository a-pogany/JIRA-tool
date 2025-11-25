"""
LLM prompts for Extraction and Review agents
"""

EXTRACTION_PROMPT = """
You are a technical product manager extracting FIRST-CLASS Jira tickets from text.

Text:
{text}

Project Key: {project_key}

EXTRACTION CHECKLIST - Extract ALL of the following:

1. **EPICS** (High-level features/initiatives)
   - Clear title (5-200 chars)
   - Detailed description (WHY this matters)
   - Business value (WHO benefits, WHAT value)
   - Priority (High/Medium/Low)

2. **TASKS** (Actionable work items under epics)
   - Specific title describing WHAT to build
   - Detailed description with technical context
   - 5+ acceptance criteria (functional, security, performance, edge cases, testing)
   - Technical notes (APIs, schemas, dependencies)
   - Priority: MUST be "High", "Medium", or "Low" (exactly these values)
   - Estimated effort: MUST be "Small", "Medium", or "Large" (exactly these values)

3. **IMPLICIT REQUIREMENTS** (Add if not mentioned):
   - Error handling and validation
   - Security (authentication, authorization, input validation)
   - Performance (response times, caching, optimization)
   - Testing (unit, integration, E2E)
   - Database migrations (if schema changes)
   - Monitoring and logging
   - Documentation updates

QUALITY STANDARDS:
- Each task MUST have AT LEAST 5 acceptance criteria
- Acceptance criteria must be specific and testable
- Include technical details (database schemas, API contracts, error messages)
- Specify exact technologies (React hooks, PostgreSQL, Redis, etc.)
- Include security requirements (rate limiting, input validation, audit logs)
- Add performance metrics where relevant (< 200ms response, 1000 req/sec)
- Think about edge cases and error scenarios
- Different software modules (batches, services, front-end) must go to separate tickets

Return as JSON:
{{
  "epics": [
    {{
      "title": "User Authentication System",
      "description": "Secure user authentication with email/password and password reset",
      "business_value": "Enables user account management and secure access control",
      "priority": "High",
      "tasks": [
        {{
          "title": "Implement login endpoint with JWT authentication",
          "description": "Create POST /api/auth/login endpoint that validates credentials and returns JWT tokens",
          "acceptance_criteria": [
            "Functional: POST /api/auth/login accepts email and password, returns access + refresh tokens",
            "Security: Passwords validated using bcrypt with minimum 8 characters",
            "Security: Rate limiting of 5 attempts per minute per IP address",
            "Error: Invalid credentials return 401 with message 'Invalid email or password'",
            "Performance: Login request completes within 200ms",
            "Testing: Unit tests for token generation and validation",
            "Edge: Handles SQL injection attempts safely",
            "Edge: Rejects requests with missing email or password fields"
          ],
          "technical_notes": "Use jsonwebtoken library, access token expires in 15min, refresh token in 7 days. Store tokens in httpOnly cookies. Database: users table with email (unique), password_hash, created_at columns.",
          "priority": "High",
          "estimated_effort": "Medium"
        }}
      ]
    }}
  ]
}}

CRITICAL:
- Be SPECIFIC: exact error messages, exact API endpoints, exact database schemas
- Be COMPLETE: security + performance + testing + error handling
- Use EXACT values for priority ("High", "Medium", "Low") and estimated_effort ("Small", "Medium", "Large")
- Think like a developer who will implement this
"""

BUG_EXTRACTION_PROMPT = """
You are a QA engineer extracting FIRST-CLASS Bug Reports from text.

Text:
{text}

Project Key: {project_key}

BUG REPORT EXTRACTION CHECKLIST - Extract ALL of the following:

1. **BUG SUMMARY** (Clear, specific title)
   - WHAT is broken (specific feature/component)
   - WHERE it occurs (which page/module)
   - WHEN it happens (under what conditions)

2. **DESCRIPTION** (Detailed problem statement)
   - Current behavior (what's happening)
   - Expected behavior (what should happen)
   - Impact on users/business

3. **REPRODUCTION STEPS** (Exact, numbered steps)
   - Step 1: Preconditions (initial state)
   - Step 2-N: Actions to reproduce
   - Must be reproducible by any developer

4. **ENVIRONMENT** (Where bug occurs)
   - Browser/OS/Device
   - Version numbers
   - User role/permissions
   - Data conditions

5. **SEVERITY & PRIORITY** (Use EXACT values)
   - Severity: MUST be "Critical", "High", "Medium", or "Low"
   - Priority: MUST be "Critical", "High", "Medium", or "Low"
   - Critical: System down, data loss, security breach
   - High: Major feature broken, workaround exists
   - Medium: Minor feature broken, low impact
   - Low: Cosmetic, typo, enhancement

6. **TECHNICAL DETAILS** (Extract if mentioned)
   - Error messages (exact text)
   - Stack traces
   - Console logs
   - Network requests (failed API calls)
   - Database state

7. **ACCEPTANCE CRITERIA** (Fix validation)
   - How to verify fix works
   - Regression test scenarios
   - Edge cases to check

Return as JSON:
{{
  "bugs": [
    {{
      "summary": "Login button does nothing when clicked on Safari iOS",
      "description": "When users click the login button on Safari iOS 15+, nothing happens. Expected: Login form should submit and redirect to dashboard. Impact: iOS users cannot access the platform.",
      "severity": "High",
      "priority": "High",
      "reproduction_steps": [
        "Open Safari on iOS 15.0+",
        "Navigate to https://app.example.com/login",
        "Enter valid email and password",
        "Click 'Login' button",
        "Observe: No action, no error, button stays in idle state"
      ],
      "environment": {{
        "browser": "Safari iOS 15.0+",
        "os": "iOS 15.0-17.0",
        "user_role": "Any",
        "data_conditions": "Valid user credentials"
      }},
      "technical_details": {{
        "error_message": "None visible",
        "console_logs": "Uncaught TypeError: Cannot read property 'submit' of null",
        "affected_code": "LoginForm.tsx line 45",
        "api_calls": "POST /api/auth/login never fires"
      }},
      "acceptance_criteria": [
        "Functional: Login button submits form on Safari iOS 15+",
        "Validation: Form validates before submission",
        "Error: Network errors show user-friendly message",
        "Regression: Works on Chrome, Firefox, Safari desktop",
        "Edge: Works with keyboard 'Enter' key submission",
        "Edge: Works with iOS autocomplete password fill"
      ],
      "suggested_fix": "Add touchend event handler for iOS compatibility"
    }}
  ]
}}

QUALITY STANDARDS:
- Each bug must have AT LEAST 5 reproduction steps
- Reproduction steps must be exact and specific
- Include technical details if available
- Acceptance criteria must verify fix works
- Think about regression testing and edge cases
"""

STORY_EXTRACTION_PROMPT = """
You are an agile product owner extracting User Stories from text.

Text:
{text}

Project Key: {project_key}

USER STORY EXTRACTION CHECKLIST:

1. **USER STORY FORMAT**
   - As a [role/persona]
   - I want to [action/feature]
   - So that [business value/benefit]

2. **ACCEPTANCE CRITERIA** (Specific, testable)
   - At least 3 criteria
   - Cover happy path and edge cases
   - Include validation and error scenarios

3. **TECHNICAL NOTES** (Implementation hints)
   - APIs, components, dependencies
   - Data requirements
   - Integration points

Return as JSON:
{{
  "stories": [
    {{
      "title": "User can reset forgotten password via email",
      "as_a": "registered user who forgot their password",
      "i_want_to": "receive a password reset link via email",
      "so_that": "I can regain access to my account securely",
      "acceptance_criteria": [
        "Given I'm on the login page, when I click 'Forgot Password', then I see a password reset form",
        "Given I enter my registered email, when I submit, then I receive a reset link within 5 minutes",
        "Given I click the reset link, when the link is valid, then I can set a new password",
        "Given the reset link is >1 hour old, when I click it, then I see 'Link expired' error",
        "Given I set a new password, when I submit, then I can login with the new password"
      ],
      "priority": "High",
      "estimated_effort": "Medium",
      "technical_notes": "Generate secure token with 1-hour expiry, send via email service (SendGrid/Mailgun), invalidate token after use"
    }}
  ]
}}

QUALITY STANDARDS:
- Stories must follow "As a/I want to/So that" format
- At least 3 acceptance criteria in Given/When/Then format
- Use EXACT values for priority ("High", "Medium", "Low") and estimated_effort ("Small", "Medium", "Large")
- Include edge cases and error scenarios
"""

# ═══════════════════════════════════════════════════════
# REVIEW PROMPT (Agent 2)
# ═══════════════════════════════════════════════════════

REVIEW_PROMPT = """
You are a senior software architect conducting a THOROUGH QUALITY REVIEW of Jira tickets.

Current Structure:
{structure}

COMPREHENSIVE REVIEW CHECKLIST:

1. **COMPLETENESS CHECK** - Is ALL necessary information present?
   For EACH task/bug/story, verify:
   ✓ Does it have AT LEAST 3 detailed acceptance criteria?
   ✓ Are both success AND failure scenarios covered?
   ✓ Are input/output specifications clear?
   ✓ Are edge cases mentioned?
   ✓ Are performance/security requirements specified?
   ✓ Is technical context provided?

2. **AMBIGUITY DETECTION** - What's unclear or vague?
   Flag any:
   - Vague descriptions ("should work well", "user-friendly", "fast", "robust")
   - Missing specifics (which API? what format? how fast? what happens if...?)
   - Undefined terms (what counts as "success"?)
   - Unspecified error handling
   - Missing data validation rules

3. **CRITICAL MISSING TASKS** - What's not mentioned but REQUIRED?

   **Infrastructure & Setup:**
   - Database migrations/schema changes?
   - Environment configuration?
   - Deployment scripts?

   **Error Handling & Resilience:**
   - What happens when external APIs fail?
   - Network timeout handling?
   - Graceful degradation?

   **Security:**
   - Authentication/authorization?
   - Input sanitization?
   - SQL injection prevention?
   - Rate limiting?

   **Data & Validation:**
   - Data validation rules?
   - Data migration for existing records?
   - Backward compatibility?

   **Testing:**
   - Unit tests?
   - Integration tests?
   - Performance tests?

   **Operations:**
   - Monitoring/alerting?
   - Logging strategy?
   - Rollback procedures?

4. **CLARIFICATION QUESTIONS** - What to ask user?
   Ask SPECIFIC questions about:
   - Exact technical requirements (not "how should it work?" → "Should login use JWT or session cookies?")
   - Business logic details ("What happens if user already exists?")
   - Performance expectations ("What's acceptable response time?")
   - Error handling ("Should failed logins lock accounts? After how many attempts?")

Return as JSON:
{{
  "gaps": [
    "Task 'X' missing acceptance criteria for error cases",
    "No performance requirements specified for 'Y'"
  ],
  "ambiguities": [
    "'user-friendly interface' in Task 1 is vague - need specific UX requirements",
    "'fast response' in Task 2 - what's the target latency?"
  ],
  "missing_tasks": [
    "Add database migration task for new user_sessions table",
    "Implement rate limiting for login endpoint",
    "Add unit tests for password validation logic"
  ],
  "questions": [
    "Should login sessions use JWT tokens or server-side sessions?",
    "What's the account lockout policy? Lock after how many failed attempts?",
    "What password complexity requirements?"
  ],
  "suggestions": [
    "Consider adding 2FA support task for future security",
    "Recommend using bcrypt for password hashing"
  ],
  "production_readiness_concerns": [
    "No rollback plan specified if authentication breaks",
    "Missing backward compatibility for existing user sessions"
  ]
}}

BE THOROUGH:
- Think like a security expert (what could be exploited?)
- Think like an ops engineer (what could break in production?)
- Think like a QA tester (what edge cases exist?)
- Think like a developer (what implementation details are missing?)

Quality bar: Each ticket should be SO COMPLETE that a developer can implement it WITHOUT asking any questions.
"""

# ═══════════════════════════════════════════════════════
# REFINEMENT PROMPT (Agent 2 - Apply Feedback)
# ═══════════════════════════════════════════════════════

REFINEMENT_PROMPT = """
Refine this ticket structure based on user feedback.

Original Structure:
{structure}

User Feedback:
{feedback}

Apply the feedback and return an improved structure with:
1. Filled gaps
2. Resolved ambiguities
3. Added suggested tasks
4. Enhanced acceptance criteria
5. More specific technical details

Return the same JSON format as the extraction prompt (with "epics", "bugs", or "stories" array).
Make sure to preserve all existing information and only ADD/ENHANCE based on feedback.

CRITICAL:
- Use EXACT values for priority ("High", "Medium", "Low") and estimated_effort ("Small", "Medium", "Large")
- Maintain proper Jira issue type structure
- Add specific, measurable acceptance criteria (not vague descriptions)
"""
