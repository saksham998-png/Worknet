from flask_socketio import SocketIO, join_room, leave_room
from flask_login import current_user

# manage_session=False avoids Flask 3.x session setter errors on connect
socketio = SocketIO(cors_allowed_origins='*', manage_session=False)


def init_socketio(app):
    socketio.init_app(app)

    @socketio.on('connect')
    def on_connect():
        try:
            if current_user.is_authenticated:
                join_room(f'user_{current_user.id}')
                if current_user.workspace_id:
                    join_room(f'workspace_{current_user.workspace_id}')
        except Exception:
            pass

    @socketio.on('disconnect')
    def on_disconnect():
        try:
            if current_user.is_authenticated:
                leave_room(f'user_{current_user.id}')
                if current_user.workspace_id:
                    leave_room(f'workspace_{current_user.workspace_id}')
        except Exception:
            pass

    @socketio.on('join_project')
    def on_join_project(data):
        try:
            if not current_user.is_authenticated:
                return
            project_id = (data or {}).get('project_id')
            if project_id:
                join_room(f'project_{project_id}')
        except Exception:
            pass

    return socketio


def emit_task_update(project_id, payload):
    try:
        socketio.emit('task_updated', payload, room=f'project_{project_id}')
    except Exception as exc:
        print(f'[WorkNet] Socket emit skipped: {exc}')


def emit_activity(workspace_id, payload):
    if not workspace_id:
        return
    try:
        socketio.emit('new_activity', payload, room=f'workspace_{workspace_id}')
    except Exception as exc:
        print(f'[WorkNet] Socket emit skipped: {exc}')
