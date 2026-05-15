from flask import Blueprint, request, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from models import db, Project, Membership, User, Task

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Project name is required.', 'danger')
        return redirect(url_for('main.dashboard'))

    project = Project(name=name, description=description, owner=current_user)
    db.session.add(project)
    db.session.flush()
    membership = Membership(user=current_user, project=project, role='Admin')
    db.session.add(membership)
    db.session.commit()

    flash('Project created successfully.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))

@projects_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.options(
        joinedload(Project.tasks).joinedload(Task.comments),
        joinedload(Project.tasks).joinedload(Task.attachments),
        joinedload(Project.memberships)
    ).get_or_404(project_id)

    if current_user not in project.members:
        abort(403)

    can_manage = project.can_manage(current_user)
    return render_template('projects/project.html', project=project, can_manage=can_manage)

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

    flash(f'{user.username} was added to the team.', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))
