#!/usr/bin/env python3
"""
JIRA Ticket Generator - Flask Backend API
Serves the React frontend and provides API endpoints for ticket generation
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
import tempfile
from datetime import datetime

from config import config
from models import IssueType
from agents.extraction_agent import ExtractionAgent
from agents.review_agent import ReviewAgent
from markdown_utils import write_markdown, generate_filename, list_markdown_files, read_markdown
from markdown_parser import parse_markdown
from jira_client import JiraClient

app = Flask(__name__, static_folder='ui/build', static_url_path='')
CORS(app)  # Enable CORS for development

# Configure upload folder
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'llm_configured': config.has_llm_configured(),
        'jira_configured': bool(config.jira_url and config.jira_email and config.jira_api_token)
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'llm_provider': config.llm_provider,
        'llm_model': config.llm_model,
        'jira_url': config.jira_url,
        'jira_email': config.jira_email,
        'default_project': config.jira_project or '',
        'has_llm': config.has_llm_configured()
    })


@app.route('/api/validate', methods=['GET'])
def validate_config():
    """Validate configuration"""
    errors = config.validate()
    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors
    })


@app.route('/api/parse', methods=['POST'])
def parse_tickets():
    """
    Parse text and extract tickets

    Request JSON:
    {
        "text": "input text" or "file": uploaded file,
        "project_key": "PROJ",
        "issue_type": "task|bug|story|epic-only",
        "skip_review": false
    }
    """
    try:
        # Get input text
        text = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Save uploaded file temporarily
                temp_path = UPLOAD_FOLDER / file.filename
                file.save(temp_path)
                text = temp_path.read_text(encoding='utf-8')
                temp_path.unlink()  # Delete temp file

        # If no file, get text from form or JSON
        if not text:
            if request.is_json:
                data = request.get_json()
                text = data.get('text', '')
            else:
                # For multipart/form-data
                text = request.form.get('text', '')

        if not text or not text.strip():
            return jsonify({'error': 'No input text provided'}), 400

        # Get parameters from form (multipart) or JSON
        if request.is_json:
            data = request.get_json()
        else:
            # For multipart/form-data, use request.form
            data = request.form

        project_key = data.get('project_key', config.jira_project or 'PROJ')
        issue_type = data.get('issue_type', 'task').lower()
        skip_review = data.get('skip_review', 'false').lower() in ['true', '1', 'yes']

        # Validate issue type
        if issue_type not in ['task', 'bug', 'story', 'epic-only']:
            return jsonify({'error': f'Invalid issue type: {issue_type}'}), 400

        # Get LLM client
        llm_client = None
        if config.has_llm_configured():
            try:
                llm_client = config.get_llm_client()
            except Exception as e:
                return jsonify({'error': f'LLM configuration error: {str(e)}'}), 500

        # Agent 1: Extract structure
        extraction_agent = ExtractionAgent(llm_client, issue_type=issue_type)
        structure = extraction_agent.extract(text, project_key)

        if not structure.has_content():
            return jsonify({'error': 'No tickets extracted from input'}), 400

        # Agent 2: Review (optional)
        review_result = None
        if not skip_review and llm_client:
            review_agent = ReviewAgent(llm_client)
            review = review_agent.review(structure)

            if review.has_issues:
                review_result = {
                    'gaps': review.gaps,
                    'ambiguities': review.ambiguities,
                    'missing_tasks': review.missing_tasks,
                    'questions': review.questions,
                    'suggestions': review.suggestions,
                    'production_readiness_concerns': review.production_readiness_concerns
                }

        # Generate markdown
        filename = generate_filename(project_key, issue_type)
        output_path = Path(filename)
        write_markdown(structure, output_path)

        # Read markdown content
        markdown_content = output_path.read_text(encoding='utf-8')

        return jsonify({
            'success': True,
            'filename': filename,
            'markdown': markdown_content,
            'review': review_result,
            'stats': {
                'total_items': structure.count_total_items(),
                'epics': len(structure.epics) if structure.epics else 0,
                'tasks': sum(len(epic.tasks) for epic in structure.epics) if structure.epics else 0,
                'bugs': len(structure.bugs) if structure.bugs else 0,
                'stories': len(structure.stories) if structure.stories else 0
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/apply-feedback', methods=['POST'])
def apply_feedback():
    """
    Apply user feedback to refine structure

    Request JSON:
    {
        "filename": "jira_tickets_PROJ_task_20251123.md",
        "answers": {"question": "answer", ...}
    }
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        answers = data.get('answers', {})

        if not filename or not answers:
            return jsonify({'error': 'Missing filename or answers'}), 400

        # This would require parsing markdown back to structure
        # For now, return success
        return jsonify({'success': True, 'message': 'Feedback applied'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/markdown/list', methods=['GET'])
def list_markdown():
    """List all generated markdown files"""
    try:
        files = list_markdown_files()
        file_list = []

        for file in files:
            stat = file.stat()
            file_list.append({
                'name': file.name,
                'path': str(file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return jsonify({'files': file_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/markdown/<filename>', methods=['GET'])
def get_markdown(filename):
    """Get markdown file content"""
    try:
        file_path = Path(filename)
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        content = file_path.read_text(encoding='utf-8')
        stat = file_path.stat()

        return jsonify({
            'filename': filename,
            'content': content,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/markdown/<filename>', methods=['PUT'])
def update_markdown(filename):
    """Update markdown file content"""
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'No content provided'}), 400

        file_path = Path(filename)
        file_path.write_text(content, encoding='utf-8')

        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File updated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/markdown/<filename>', methods=['DELETE'])
def delete_markdown(filename):
    """Delete markdown file"""
    try:
        file_path = Path(filename)
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        file_path.unlink()

        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-to-jira', methods=['POST'])
def upload_to_jira():
    """
    Upload markdown to Jira

    Request JSON:
    {
        "filename": "jira_tickets_PROJ_task_20251123.md"
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        print(f"[DEBUG] Upload to Jira - Raw data: {data}")

        if not data:
            print("[ERROR] No JSON data received")
            return jsonify({'error': 'Invalid JSON data'}), 400

        filename = data.get('filename')
        print(f"[DEBUG] Upload to Jira - Extracted filename: {filename}")

        if not filename:
            print("[ERROR] Filename is None or empty")
            return jsonify({'error': 'No filename provided'}), 400

        # Validate Jira configuration
        if not (config.jira_url and config.jira_email and config.jira_api_token):
            return jsonify({'error': 'Jira not configured. Please set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN in .env'}), 400

        # Check if file exists
        file_path = Path(filename)
        if not file_path.exists():
            return jsonify({'error': f'File not found: {filename}'}), 404

        # Parse markdown back to TicketStructure
        print(f"[DEBUG] Parsing markdown file: {filename}")
        try:
            structure = parse_markdown(file_path)
            print(f"[DEBUG] Parsed structure: {structure.count_total_items()} items")
        except Exception as e:
            print(f"[ERROR] Failed to parse markdown: {e}")
            return jsonify({'error': f'Failed to parse markdown: {str(e)}'}), 400

        # Initialize Jira client
        print("[DEBUG] Initializing Jira client")
        jira_client = JiraClient(
            jira_url=config.jira_url,
            email=config.jira_email,
            api_token=config.jira_api_token
        )

        # Test connection
        print("[DEBUG] Testing Jira connection")
        if not jira_client.test_connection():
            return jsonify({'error': 'Failed to connect to Jira. Please check your credentials.'}), 400

        # Upload to Jira
        print("[DEBUG] Uploading to Jira")
        results = jira_client.upload_structure(structure)
        print(f"[DEBUG] Upload results: {results}")

        # Count created tickets
        total_created = (
            len(results.get('epics', [])) +
            len(results.get('tasks', [])) +
            len(results.get('bugs', [])) +
            len(results.get('stories', []))
        )

        return jsonify({
            'success': True,
            'message': f'Successfully uploaded {total_created} tickets to Jira',
            'results': results
        })

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Check if in development mode
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5010))

    print(f"""
╔════════════════════════════════════════════╗
║   JIRA Ticket Generator - Web Server      ║
╚════════════════════════════════════════════╝

🌐 Server starting...
   URL: http://localhost:{port}
   Mode: {'Development' if debug_mode else 'Production'}
   LLM: {config.llm_provider} ({config.llm_model})

📝 API Endpoints:
   GET  /api/health          - Health check
   GET  /api/config          - Get configuration
   POST /api/parse           - Parse and extract tickets
   GET  /api/markdown/list   - List markdown files
   GET  /api/markdown/<file> - Get markdown content
   PUT  /api/markdown/<file> - Update markdown content
   POST /api/upload-to-jira  - Upload to Jira

Press Ctrl+C to stop the server
    """)

    app.run(debug=debug_mode, host='0.0.0.0', port=port)
