import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)

from backend.app import app, create_app

# Ensure app is created
if not app:
    app = create_app()

# Export for gunicorn
__all__ = ['app']
