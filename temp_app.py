from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/var/www/question_bank/flask_debug.log'
)

app = Flask(__name__)

# Log all requests for debugging
@app.before_request
def log_request():
    logging.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.route('/')
def index():
    logging.info("Index page accessed")
    return """
    <html><body>
    <h1>Emergency Mode</h1>
    <p>Server is in emergency mode.</p>
    <p><a href="/smart_paper">Go to Smart Paper</a></p>
    </body></html>
    """

# Smart paper route that works without the template
@app.route('/smart_paper')
def smart_paper():
    logging.info("Smart paper page accessed")
    return """
    <html><body>
    <h1>Smart Paper</h1>
    <p>This is a temporary Smart Paper page.</p>
    <p>The server is being repaired and will be back to normal soon.</p>
    </body></html>
    """

# Catch-all route that logs missing pages
@app.route('/<path:path>')
def catch_all(path):
    logging.warning(f"Tried to access missing path: {path}")
    return f"The path /{path} was not found. Server is in emergency mode."

if __name__ == '__main__':
    app.run(debug=True)
