import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from backend.models import db, Project, Task, SavedView, Comment, Attachment, Membership

views_bp = Blueprint('views', __name__)


def _get_project(project_id):
    project = Project.query.options(
        joinedload(Project.tasks).joinedload(Task.assignee),
        joinedload(Project.memberships).joinedload(Membership.user),
    ).get_or_404(project_id)
    if current_user not in project.members:
        abort(403)
    return project


def _filter_tasks(tasks, filters):
    result = list(tasks)
    status = filters.get('status')
    priority = filters.get('priority')
    assignee = filters.get('assignee')
    search = (filters.get('search') or '').lower()

    if status and status != 'all':
        result = [t for t in result if t.status.lower() == status.lower()]
    if priority and priority != 'all':
        result = [t for t in result if t.priority.lower() == priority.lower()]
    if assignee == 'me':
        result = [t for t in result if t.assignee_id == current_user.id]
    elif assignee == 'unassigned':
        result = [t for t in result if not t.assignee_id]
    if search:
        result = [
            t for t in result
            if search in t.title.lower()
            or (t.assignee and search in t.assignee.username.lower())
        ]
    return result


@views_bp.route('/projects/<int:project_id>/kanban')
@login_required
def kanban(project_id):
    project = _get_project(project_id)
    tasks_by_status = {
        'To Do': sorted([t for t in project.tasks if t.status == 'To Do'], key=lambda x: x.sort_order),
        'In Progress': sorted([t for t in project.tasks if t.status == 'In Progress'], key=lambda x: x.sort_order),
        'Done': sorted([t for t in project.tasks if t.status == 'Done'], key=lambda x: x.sort_order),
    }
    saved_views = SavedView.query.filter_by(user_id=current_user.id, project_id=project.id).all()
    return render_template(
        'projects/kanban.html',
        project=project,
        tasks_by_status=tasks_by_status,
        can_manage=project.can_manage(current_user),
        saved_views=saved_views,
    )


@views_bp.route('/projects/<int:project_id>/calendar')
@login_required
def calendar_view(project_id):
    project = _get_project(project_id)
    tasks_with_dates = [t for t in project.tasks if t.due_date]
    return render_template(
        'projects/calendar.html',
        project=project,
        tasks=tasks_with_dates,
        can_manage=project.can_manage(current_user),
    )


@views_bp.route('/projects/<int:project_id>/filters', methods=['POST'])
@login_required
def save_filter_view(project_id):
    project = _get_project(project_id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('View name is required.', 'danger')
        return redirect(request.referrer or url_for('projects.project_detail', project_id=project.id))

    filters = {
        'status': request.form.get('status', 'all'),
        'priority': request.form.get('priority', 'all'),
        'assignee': request.form.get('assignee', 'all'),
        'search': request.form.get('search', ''),
    }
    view = SavedView(name=name, user_id=current_user.id, project_id=project.id)
    view.filters = filters
    db.session.add(view)
    db.session.commit()
    flash(f'Saved view "{name}" created.', 'success')
    return redirect(request.referrer or url_for('views.kanban', project_id=project.id))


@views_bp.route('/projects/<int:project_id>/filters/<int:view_id>/apply')
@login_required
def apply_saved_view(project_id, view_id):
    project = _get_project(project_id)
    view = SavedView.query.filter_by(id=view_id, user_id=current_user.id, project_id=project.id).first_or_404()
    filtered = _filter_tasks(project.tasks, view.filters)
    return render_template(
        'projects/filtered.html',
        project=project,
        tasks=filtered,
        view=view,
        can_manage=project.can_manage(current_user),
    )
