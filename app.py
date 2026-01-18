import os
import logging
from flask import Flask, request, render_template_string
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template to display the authorization code
CALLBACK_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OAuth Authorization Success</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #2d3748;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .success-icon {
            color: #48bb78;
            font-size: 2em;
        }
        .service-badge {
            display: inline-block;
            background: #4299e1;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            margin-left: 10px;
        }
        .code-box {
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            word-break: break-all;
            color: #2d3748;
        }
        .code-label {
            color: #718096;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .instructions {
            background: #edf2f7;
            border-left: 4px solid #4299e1;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }
        .instructions ol {
            margin: 10px 0 0 0;
            padding-left: 20px;
        }
        .instructions li {
            margin: 8px 0;
            color: #2d3748;
        }
        .copy-btn {
            background: #4299e1;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
            width: 100%;
            margin-top: 10px;
        }
        .copy-btn:hover {
            background: #3182ce;
        }
        .copy-btn:active {
            background: #2c5282;
        }
        .copied {
            background: #48bb78 !important;
        }
        .error {
            color: #e53e3e;
            background: #fff5f5;
            border: 2px solid #fc8181;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .debug-info {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
            font-size: 13px;
            color: #2d3748;
        }
        .debug-info strong {
            color: #4299e1;
        }
        .debug-info pre {
            background: #edf2f7;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if code %}
            <h1>
                <span class="success-icon">✓</span> 
                Authorization Successful!
                {% if service %}
                <span class="service-badge">{{ service }}</span>
                {% endif %}
            </h1>
            <p>Your OAuth authorization was successful. Copy the code below and paste it into your application.</p>

            <div class="code-label">Authorization Code:</div>
            <div class="code-box" id="authCode">{{ code }}</div>

            <button class="copy-btn" onclick="copyCode()">📋 Copy Code to Clipboard</button>

            <div class="instructions">
                <strong>Next Steps:</strong>
                <ol>
                    <li>Copy the authorization code above</li>
                    <li>Go back to your application</li>
                    <li>Paste the code when prompted</li>
                    <li>Your app will exchange it for an access token</li>
                </ol>
            </div>
        {% else %}
            <h1><span style="color: #e53e3e;">✗</span> No Authorization Code Found</h1>
            <div class="error">
                <strong>The callback was received but no authorization code was found.</strong>
                <p>This could mean:</p>
                <ul>
                    <li>The OAuth provider sent an error</li>
                    <li>The authorization was denied</li>
                    <li>There's a configuration mismatch</li>
                </ul>
            </div>
        {% endif %}

        <div class="debug-info">
            <strong>🔍 Debug Information</strong><br>
            <strong>Timestamp:</strong> {{ timestamp }}<br>
            <strong>Request URL:</strong> {{ request_url }}<br>
            <strong>Request Path:</strong> {{ request_path }}<br>

            {% if all_params %}
            <strong>All Query Parameters Received:</strong>
            <pre>{{ all_params }}</pre>
            {% else %}
            <strong>Query Parameters:</strong> None received
            {% endif %}

            {% if headers %}
            <strong>Request Headers:</strong>
            <pre>{{ headers }}</pre>
            {% endif %}
        </div>
    </div>

    <script>
        function copyCode() {
            const code = document.getElementById('authCode').textContent;
            navigator.clipboard.writeText(code).then(function() {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✓ Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = '📋 Copy Code to Clipboard';
                    btn.classList.remove('copied');
                }, 2000);
            }, function(err) {
                alert('Failed to copy: ' + err);
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    """Home page - shows that the server is running"""
    logger.info("Home page accessed")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Callback Server</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                color: white;
                text-align: center;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            h1 { margin: 0 0 20px 0; }
            p { font-size: 18px; opacity: 0.9; }
            .service-list {
                margin-top: 30px;
                text-align: left;
                display: inline-block;
            }
            .service-list li {
                margin: 10px 0;
            }
            .test-link {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 10px;
                text-decoration: none;
                color: white;
                transition: background 0.3s;
            }
            .test-link:hover {
                background: rgba(255,255,255,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 OAuth Callback Server</h1>
            <p>Server is running and ready to receive OAuth callbacks.</p>
            <div class="service-list">
                <strong>Supported Services:</strong>
                <ul>
                    <li>Whoop API</li>
                    <li>Suunto API</li>
                    <li>Any OAuth 2.0 service</li>
                </ul>
            </div>
            <p style="font-size: 14px; margin-top: 30px;">
                This page will automatically display your authorization code when you complete the OAuth flow.
            </p>
            <a href="/callback?code=test123&state=test" class="test-link">
                🧪 Test Callback Page
            </a>
        </div>
    </body>
    </html>
    """


@app.route('/callback')
def callback():
    """
    OAuth callback endpoint - receives authorization code from OAuth providers
    Works with Whoop, Suunto, and other OAuth 2.0 services
    """
    # Log that we received a callback
    logger.info("=" * 60)
    logger.info("CALLBACK ENDPOINT HIT!")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info(f"Full URL: {request.url}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Query String: {request.query_string.decode()}")
    logger.info(f"Args: {dict(request.args)}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Remote Address: {request.remote_addr}")
    logger.info("=" * 60)

    # Get the authorization code from the query parameters
    code = request.args.get('code')
    error = request.args.get('error')

    # Try to identify the service (optional, for display purposes)
    state = request.args.get('state', '')
    service = None
    if 'whoop' in state.lower():
        service = 'Whoop'
    elif 'suunto' in state.lower():
        service = 'Suunto'

    # Collect all debug information
    all_params = dict(request.args) if request.args else None
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ['cookie', 'authorization']}

    # Format for display
    import json
    all_params_str = json.dumps(all_params, indent=2) if all_params else "None"
    headers_str = json.dumps(headers, indent=2) if headers else "None"

    logger.info(f"Code found: {code is not None}")
    logger.info(f"Error found: {error is not None}")

    # Render the callback page with all debug info
    return render_template_string(
        CALLBACK_TEMPLATE,
        code=code,
        service=service,
        timestamp=datetime.now().isoformat(),
        request_url=request.url,
        request_path=request.path,
        all_params=all_params_str,
        headers=headers_str
    )


@app.route('/health')
def health():
    """Health check endpoint for Render"""
    logger.info("Health check accessed")
    return {'status': 'healthy', 'message': 'OAuth callback server is running'}, 200


# Catch-all route to see if requests are going to wrong endpoints
@app.route('/<path:path>')
def catch_all(path):
    """Catch any other routes"""
    logger.warning(f"Unknown path accessed: /{path}")
    logger.warning(f"Full URL: {request.url}")
    logger.warning(f"Query params: {dict(request.args)}")
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 50px;
                background: #f7fafc;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #e53e3e; }}
            .info {{ background: #edf2f7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Unknown Path</h1>
            <p>The path <code>/{path}</code> was accessed but is not configured.</p>
            <div class="info">
                <strong>Available endpoints:</strong><br>
                • <a href="/">/</a> - Home page<br>
                • <a href="/callback">/callback</a> - OAuth callback<br>
                • <a href="/health">/health</a> - Health check
            </div>
            <div class="info">
                <strong>Request Details:</strong><br>
                Path: /{path}<br>
                Full URL: {request.url}<br>
                Query params: {dict(request.args)}
            </div>
        </div>
    </body>
    </html>
    """, 404


if __name__ == '__main__':
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 8080))

    # Determine if we're in development or production
    is_production = os.environ.get('RENDER') is not None

    logger.info(f"Starting server on port {port}")
    logger.info(f"Production mode: {is_production}")

    if is_production:
        # Production: Use Gunicorn (configure in Render)
        app.run(host='0.0.0.0', port=port)
    else:
        # Local development
        app.run(debug=True, host='0.0.0.0', port=port)