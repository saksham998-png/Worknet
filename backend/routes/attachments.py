import os
from flask import Blueprint, request, redirect, url_for, flash, abort, send_from_directory, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db, Attachment, Task
from utils.activity_logger import log_activity

attachments_bp = Blueprint('attachments', __name__)

@attachments_bp.route('/tasks/<int:task_id>/attachments', methods=['POST'])
@login_required
def upload_attachment(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user not in task.project.members:
        abort(403)

    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=task.project.id))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=task.project.id))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(file_path)

        attachment = Attachment(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.mimetype or 'application/octet-stream',
            task=task,
            uploader=current_user
        )
        db.session.add(attachment)
        db.session.commit()

        # Log activity
        log_activity(
            current_user,
            'uploaded_file',
            f'Uploaded file "{filename}" to task "{task.title}"',
            project=task.project,
            task=task
        )

        flash('File uploaded successfully.', 'success')

    return redirect(url_for('projects.project_detail', project_id=task.project.id))

@attachments_bp.route('/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    if current_user not in attachment.task.project.members:
        abort(403)

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        os.path.basename(attachment.file_path),
        as_attachment=True,
        download_name=attachment.original_filename
    )

@attachments_bp.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    if current_user != attachment.uploader and not attachment.task.project.can_manage(current_user):
        abort(403)

    task = attachment.task
    project = task.project
    filename = attachment.filename

    # Remove file from filesystem
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    db.session.delete(attachment)
    db.session.commit()

    # Log activity
    log_activity(
        current_user,
        'deleted_file',
        f'Deleted file "{filename}" from task "{task.title}"',
        project=project,
        task=task
    )

    flash('File deleted.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))
