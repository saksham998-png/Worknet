from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from backend.models import db, Project, Task, Activity, SavedView, Notification
from backend.utils.activity_logger import log_activity
from backend.utils.socketio_events import emit_task_update, emit_activity

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/projects', methods=['GET'])
@login_required
def api_projects():
    return jsonify([project.to_dict() for project in current_user.projects])


@api_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@login_required
def api_project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.members:
        abort(403)
    return jsonify([task.to_dict() for task in project.tasks])


@api_bp.route('/api/tasks/<int:task_id>', methods=['GET', 'PATCH'])
@login_required
def api_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user not in task.project.members:
        abort(403)

    if request.method == 'GET':
        return jsonify(task.to_dict())

    if current_user != task.assignee and not task.project.can_manage(current_user):
        return jsonify({'message': 'Forbidden'}), 403

    data = request.get_json() or {}
    status = data.get('status')
    priority = data.get('priority')
    sort_order = data.get('sort_order')

    if status and status not in ['To Do', 'In Progress', 'Done']:
        return jsonify({'message': 'Invalid status'}), 400
    if priority and priority not in ['Low', 'Medium', 'High', 'Urgent']:
        return jsonify({'message': 'Invalid priority'}), 400

    changes = []
    if status:
        task.status = status
        changes.append(f'status to "{status}"')
    if priority:
        task.priority = priority
        changes.append(f'priority to "{priority}"')
    if sort_order is not None:
        task.sort_order = int(sort_order)

    db.session.commit()

    if changes:
        log_activity(current_user, 'updated_task', f'Updated task: {", ".join(changes)}', project=task.project, task=task)
        payload = task.to_dict()
        emit_task_update(task.project_id, payload)
        emit_activity(current_user.workspace_id, {'action': 'updated_task', 'task_id': task.id})

    return jsonify(task.to_dict())


@api_bp.route('/api/projects/<int:project_id>/tasks/reorder', methods=['POST'])
@login_required
def api_reorder_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.can_manage(current_user) and current_user not in project.members:
        abort(403)

    data = request.get_json() or {}
    items = data.get('items', [])
    for item in items:
        task = Task.query.filter_by(id=item.get('id'), project_id=project_id).first()
        if task:
            if 'status' in item:
                task.status = item['status']
            if 'sort_order' in item:
                task.sort_order = item['sort_order']
    db.session.commit()
    emit_task_update(project_id, {'reordered': True})
    return jsonify({'success': True})


@api_bp.route('/api/projects/<int:project_id>/activities', methods=['GET'])
@login_required
def api_project_activities(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.members:
        abort(403)

    activities = Activity.query.filter_by(project_id=project_id).order_by(
        Activity.created_at.desc()
    ).limit(50).all()
    return jsonify([_activity_dict(a) for a in activities])


@api_bp.route('/api/activity', methods=['GET'])
@login_required
def api_workspace_activity():
    query = Activity.query
    if current_user.workspace_id:
        query = query.filter_by(workspace_id=current_user.workspace_id)
    else:
        query = query.filter_by(user_id=current_user.id)
    activities = query.order_by(Activity.created_at.desc()).limit(50).all()
    return jsonify([_activity_dict(a) for a in activities])


@api_bp.route('/api/notifications', methods=['GET'])
@login_required
def api_notifications():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(30).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'read': n.read,
        'created_at': n.created_at.isoformat(),
    } for n in items])


@api_bp.route('/api/notifications/<int:nid>/read', methods=['POST'])
@login_required
def mark_notification_read(nid):
    n = Notification.query.filter_by(id=nid, user_id=current_user.id).first_or_404()
    n.read = True
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/api/projects/<int:project_id>/members', methods=['GET'])
@login_required
def api_project_members(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.members:
        abort(403)
    return jsonify([{'id': m.id, 'username': m.username, 'email': m.email} for m in project.members])


@api_bp.route('/api/saved-views', methods=['GET'])
@login_required
def api_saved_views():
    views = SavedView.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'project_id': v.project_id,
        'filters': v.filters,
    } for v in views])


def _activity_dict(activity):
    return {
        'id': activity.id,
        'action': activity.action,
        'description': activity.description,
        'created_at': activity.created_at.isoformat(),
        'user': activity.user.username,
        'task_title': activity.task.title if activity.task else None,
        'project_name': activity.project.name if activity.project else None,
    }
