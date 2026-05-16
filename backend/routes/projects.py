from flask import Blueprint, request, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from backend.models import db, Project, Membership, User, Task, Comment, Attachment, SavedView
from backend.utils.audit import log_audit

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Project name is required.', 'danger')
        return redirect(url_for('main.dashboard'))

    project = Project(
        name=name,
        description=description,
        owner=current_user,
        workspace=current_user.workspace,
    )
    db.session.add(project)
    db.session.flush()
    membership = Membership(user=current_user, project=project, role='Admin')
    db.session.add(membership)
    db.session.commit()
    log_audit(current_user, 'project_created', f'Created project {name}', current_user.workspace)

    flash('Project created successfully.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))


@projects_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.options(
        joinedload(Project.tasks).joinedload(Task.comments).joinedload(Comment.author),
        joinedload(Project.tasks).joinedload(Task.attachments).joinedload(Attachment.uploader),
        joinedload(Project.tasks).joinedload(Task.assignee),
        joinedload(Project.tasks).joinedload(Task.creator),
        joinedload(Project.memberships).joinedload(Membership.user),
    ).get_or_404(project_id)

    if current_user not in project.members:
        abort(403)

    can_manage = project.can_manage(current_user)
    saved_views = SavedView.query.filter_by(user_id=current_user.id, project_id=project.id).all()
    return render_template(
        'projects/project.html',
        project=project,
        can_manage=can_manage,
        saved_views=saved_views,
    )
@projects_bp.route('/projects/<int:project_id>/edit', methods=['POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.can_manage(current_user):
        abort(403)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Active')

    if not name:
        flash('Project name is required.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    project.name = name
    project.description = description
    
    if status in ['Active', 'Paused', 'Archived']:
        project.status = status

    db.session.commit()
    log_audit(current_user, 'project_edited', f'Edited project {name}', current_user.workspace)

    flash('Project updated successfully.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))


@projects_bp.route('/projects/<int:project_id>/members/add', methods=['POST'])
@login_required
def add_project_member(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.can_manage(current_user):
        abort(403)

    email = request.form.get('email', '').strip().lower()
    role = request.form.get('role', 'Member')
    user = User.query.filter_by(email=email).first()

    if user is None:
        flash('No user found with that email address.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    if user in project.members:
        flash('User is already a member of the project.', 'warning')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    membership = Membership(user=user, project=project, role='Admin' if role == 'Admin' else 'Member')
    db.session.add(membership)
    db.session.commit()
    log_audit(current_user, 'member_added', f'Added {user.email} to {project.name}', current_user.workspace)

    flash(f'{user.username} was added to the team.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))
