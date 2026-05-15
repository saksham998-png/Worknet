from flask import Blueprint, render_template, abort, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, Project, Activity

admin_bp = Blueprint('admin', __name__)

def _require_admin():
    if current_user.role != 'Admin':
        abort(403)

@admin_bp.route('/admin')
@login_required
def dashboard():
    _require_admin()

    users = User.query.order_by(User.created_at.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(20).all()

    return render_template(
        'admin/dashboard.html',
        users=users,
        projects=projects,
        recent_activities=recent_activities,
    )

@admin_bp.route('/admin/users/<int:user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    _require_admin()

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own admin role here.', 'warning')
        return redirect(url_for('admin.dashboard'))

    role = request.form.get('role', '')
    if role not in ['Admin', 'Member']:
        flash('Invalid role selection.', 'danger')
        return redirect(url_for('admin.dashboard'))

    user.role = role
    db.session.commit()
    flash(f"{user.username}'s role has been updated to {role}.", 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/projects/<int:project_id>/status', methods=['POST'])
@login_required
def update_project_status(project_id):
    _require_admin()

    project = Project.query.get_or_404(project_id)
    status = request.form.get('status', '')
    if status not in ['Active', 'Paused', 'Archived']:
        flash('Invalid project status.', 'danger')
        return redirect(url_for('admin.dashboard'))

    project.status = status
    db.session.commit()
    flash(f"{project.name} status updated to {status}.", 'success')
    return redirect(url_for('admin.dashboard'))
