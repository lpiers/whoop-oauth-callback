from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template to display the authorization code
CALLBACK_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whoop Authorization Success</title>
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
    </style>
</head>
<body>
    <div class="container">
        {% if code %}
            <h1><span class="success-icon">✓</span> Authorization Successful!</h1>
            <p>Your Whoop API authorization was successful. Copy the code below and paste it into your Python script.</p>
            
            <div class="code-label">Authorization Code:</div>
            <div class="code-box" id="authCode">{{ code }}</div>
            
            <button class="copy-btn" onclick="copyCode()">📋 Copy Code to Clipboard</button>
            
            <div class="instructions">
                <strong>Next Steps:</strong>
                <ol>
                    <li>Copy the authorization code above</li>
                    <li>Go back to your Python script</li>
                    <li>Paste the code when prompted</li>
                    <li>Your script will exchange it for an access token</li>
                </ol>
            </div>
        {% else %}
            <h1><span style="color: #e53e3e;">✗</span> Authorization Error</h1>
            <div class="error">
                <strong>No authorization code received.</strong>
                <p>The callback was triggered but no authorization code was found in the URL.</p>
                <p>Please try the authorization process again.</p>
            </div>
        {% endif %}
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
    """Home page - just shows that the server is running"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Whoop OAuth Callback Server</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏃‍♂️ Whoop OAuth Callback Server</h1>
            <p>Server is running and ready to receive OAuth callbacks.</p>
            <p style="font-size: 14px; margin-top: 30px;">This page will automatically display your authorization code when you complete the Whoop OAuth flow.</p>
        </div>
    </body>
    </html>
    """

@app.route('/callback')
def callback():
    """
    OAuth callback endpoint - Whoop will redirect here after authorization
    Extracts the authorization code from the URL and displays it
    """
    # Get the authorization code from the query parameters
    code = request.args.get('code')
    error = request.args.get('error')
    
    # If there was an error in the OAuth flow
    if error:
        error_description = request.args.get('error_description', 'Unknown error')
        return f"""
        <html>
        <body style="font-family: Arial; padding: 50px; background: #fff5f5;">
            <h1 style="color: #e53e3e;">Authorization Failed</h1>
            <p><strong>Error:</strong> {error}</p>
            <p><strong>Description:</strong> {error_description}</p>
            <p>Please try the authorization process again.</p>
        </body>
        </html>
        """, 400
    
    # Render the success page with the authorization code
    return render_template_string(CALLBACK_TEMPLATE, code=code)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'Whoop OAuth callback server is running'}, 200

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, host='0.0.0.0', port=8080)
