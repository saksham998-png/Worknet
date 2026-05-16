import os
import sys
import importlib.util

project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)

spec = importlib.util.spec_from_file_location('backend_app', os.path.join(backend_dir, 'app.py'))
backend_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_app)
app = backend_app.app
socketio = app.socketio


def _is_debug_enabled():
    return os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}


if __name__ == '__main__':
    debug = _is_debug_enabled()
    socketio.run(
        app,
        debug=debug,
        use_reloader=debug,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        allow_unsafe_werkzeug=True,
    )
