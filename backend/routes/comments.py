from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Comment, Task
from utils.activity_logger import log_activity

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

    comment = Comment(
        content=content,
        task=task,
        author=current_user
    )
    db.session.add(comment)
    db.session.commit()

    # Log activity
    log_activity(
        current_user,
        'commented',
        f'Added a comment to task "{task.title}"',
        project=task.project,
        task=task
    )

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

    # Log activity
    log_activity(
        current_user,
        'deleted_comment',
        f'Deleted a comment from task "{task_title}"',
        project=project,
        task=task
    )

    flash('Comment deleted.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))
