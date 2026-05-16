from flask import Blueprint, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from models import db, Task, Project, User
from utils.activity_logger import log_activity
from utils.notifications import notify_user
from utils.socketio_events import emit_task_update, emit_activity

tasks_bp = Blueprint('tasks', __name__)


def _emit_task_change(task):
    emit_task_update(task.project_id, task.to_dict())
    ws_id = task.project.workspace_id if task.project else current_user.workspace_id
    emit_activity(ws_id, {'action': 'task_updated', 'task_id': task.id})


@tasks_bp.route('/projects/<int:project_id>/tasks/create', methods=['POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.can_manage(current_user):
        abort(403)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()
    assignee_email = request.form.get('assignee_email', '').strip().lower()
    priority = request.form.get('priority', 'Medium')
    assignee = User.query.filter_by(email=assignee_email).first() if assignee_email else None

    if not title:
        flash('Task title is required.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    if assignee is None and assignee_email:
        flash('Assigned user was not found.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    if assignee and assignee not in project.members:
        flash('Assignee must be a member of the project.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    if priority not in ['Low', 'Medium', 'High', 'Urgent']:
        priority = 'Medium'

    max_order = db.session.query(func.max(Task.sort_order)).filter_by(project_id=project.id).scalar() or 0

    task = Task(
        title=title,
        description=description,
        due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
        project=project,
        assignee=assignee,
        creator=current_user,
        priority=priority,
        sort_order=max_order + 1,
    )
    db.session.add(task)
    db.session.commit()

    log_activity(current_user, 'created_task', f'Created task "{task.title}"', project=project, task=task)
    if assignee:
        notify_user(assignee, 'New task assigned', f'"{title}" in {project.name}', link=f'/projects/{project.id}', email=True)
    _emit_task_change(task)

    flash('Task added successfully.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))


@tasks_bp.route('/tasks/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user != task.assignee and not task.project.can_manage(current_user):
        abort(403)

    new_status = request.form.get('status', task.status)
    if new_status not in ['To Do', 'In Progress', 'Done']:
        flash('Invalid task status.', 'danger')
    else:
        old_status = task.status
        task.status = new_status
        db.session.commit()
        log_activity(
            current_user,
            'updated_task',
            f'Changed task status from "{old_status}" to "{new_status}"',
            project=task.project,
            task=task,
        )
        _emit_task_change(task)
        flash('Task status updated.', 'success')

    return redirect(request.referrer or url_for('projects.project_detail', project_id=task.project.id))


@tasks_bp.route('/tasks/<int:task_id>/update-priority', methods=['POST'])
@login_required
def update_task_priority(task_id):
    task = Task.query.get_or_404(task_id)
    if not task.project.can_manage(current_user):
        abort(403)

    new_priority = request.form.get('priority', task.priority)
    if new_priority not in ['Low', 'Medium', 'High', 'Urgent']:
        flash('Invalid task priority.', 'danger')
    else:
        old_priority = task.priority
        task.priority = new_priority
        db.session.commit()
        log_activity(
            current_user,
            'updated_task',
            f'Changed task priority from "{old_priority}" to "{new_priority}"',
            project=task.project,
            task=task,
        )
        _emit_task_change(task)
        flash('Task priority updated.', 'success')

    return redirect(request.referrer or url_for('projects.project_detail', project_id=task.project.id))
