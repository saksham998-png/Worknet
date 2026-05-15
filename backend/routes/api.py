from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from models import db, Project, Task, Activity
from utils.activity_logger import log_activity

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

@api_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
@login_required
def api_update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user != task.assignee and not task.project.can_manage(current_user):
        return jsonify({'message': 'Forbidden'}), 403

    data = request.get_json() or {}
    status = data.get('status')
    priority = data.get('priority')

    if status and status not in ['To Do', 'In Progress', 'Done']:
        return jsonify({'message': 'Invalid status'}), 400

    if priority and priority not in ['Low', 'Medium', 'High', 'Urgent']:
        return jsonify({'message': 'Invalid priority'}), 400

    if status:
        task.status = status
    if priority:
        task.priority = priority

    db.session.commit()

    # Log activity
    changes = []
    if status:
        changes.append(f'status to "{status}"')
    if priority:
        changes.append(f'priority to "{priority}"')
    if changes:
        log_activity(
            current_user,
            'updated_task',
            f'Updated task: {", ".join(changes)}',
            project=task.project,
            task=task
        )

    return jsonify(task.to_dict())

@api_bp.route('/api/projects/<int:project_id>/activities', methods=['GET'])
@login_required
def api_project_activities(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.members:
        abort(403)

    activities = Activity.query.filter_by(project_id=project_id).order_by(Activity.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': activity.id,
        'action': activity.action,
        'description': activity.description,
        'created_at': activity.created_at.isoformat(),
        'user': activity.user.username,
        'task_title': activity.task.title if activity.task else None
    } for activity in activities])