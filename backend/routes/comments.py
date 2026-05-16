from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from backend.models import db, Comment, Task
from backend.utils.activity_logger import log_activity
from backend.utils.mentions import process_mentions
from backend.utils.notifications import notify_user, send_email_notification
from backend.utils.integrations import broadcast_event
from backend.utils.socketio_events import emit_activity

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user not in task.project.members:
        abort(403)

    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=task.project.id))

    comment = Comment(content=content, task=task, author=current_user)
    db.session.add(comment)
    db.session.flush()

    mentioned = process_mentions(comment, task.project, current_user)
    db.session.commit()

    log_activity(
        current_user,
        'commented',
        f'Added a comment to task "{task.title}"',
        project=task.project,
        task=task,
    )

    for user in mentioned:
        send_email_notification(
            user,
            f'{current_user.username} mentioned you on WorkNet',
            f'On task "{task.title}": {content}',
        )

    if task.assignee and task.assignee.id != current_user.id:
        notify_user(
            task.assignee,
            'New comment on your task',
            f'{current_user.username}: {content[:120]}',
            link=f'/projects/{task.project.id}',
        )

    workspace = task.project.workspace or current_user.workspace
    if workspace:
        broadcast_event(workspace, f'{current_user.username} commented on "{task.title}"')
        emit_activity(workspace.id, {'action': 'commented', 'task_id': task.id})

    flash('Comment added.', 'success')
    return redirect(url_for('projects.project_detail', project_id=task.project.id))


@comments_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author and not comment.task.project.can_manage(current_user):
        abort(403)

    task = comment.task
    project = task.project
    task_title = task.title
    db.session.delete(comment)
    db.session.commit()

    log_activity(
        current_user,
        'deleted_comment',
        f'Deleted a comment from task "{task_title}"',
        project=project,
        task=task,
    )

    flash('Comment deleted.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))
