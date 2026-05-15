#!/usr/bin/env python
"""
Main entry point for the WorkNet application.
This file should be run from the project root directory.
"""

import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Import and run the application
from app import app


def _is_debug_enabled():
    return os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}

if __name__ == '__main__':
    debug = _is_debug_enabled()
    app.run(
        debug=debug,
        use_reloader=debug,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
    )
