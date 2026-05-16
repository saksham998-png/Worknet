from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from backend.models import Activity, Notification, ensure_user_workspace

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        if not current_user.onboarding_completed:
            return redirect(url_for('onboarding.onboarding'))
        return redirect(url_for('main.dashboard'))
    return render_template('main/home.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.onboarding_completed:
        return redirect(url_for('onboarding.onboarding'))

    ensure_user_workspace(current_user)
    projects = current_user.projects
    all_tasks = [task for project in projects for task in project.tasks]
    today = datetime.utcnow().date()
    total_tasks = len(all_tasks)
    completed_tasks = len([task for task in all_tasks if task.status == 'Done'])
    overdue_tasks = len([task for task in all_tasks if task.is_overdue])
    pending_tasks = len([task for task in all_tasks if task.status != 'Done'])
    assigned_tasks = [task for task in all_tasks if task.assignee_id == current_user.id and task.status != 'Done']
    due_soon_tasks = [
        task for task in all_tasks
        if task.due_date and today <= task.due_date <= today + timedelta(days=3) and task.status != 'Done'
    ]
    high_priority = [t for t in all_tasks if t.priority in ('High', 'Urgent') and t.status != 'Done'][:6]

    project_snapshots = sorted(
        projects,
        key=lambda project: (
            project.task_stats['overdue'],
            -project.task_stats['completion_rate'],
            len(project.tasks),
        ),
    )[:6]

    workspace_activities = []
    if current_user.workspace_id:
        workspace_activities = Activity.query.filter_by(
            workspace_id=current_user.workspace_id
        ).order_by(Activity.created_at.desc()).limit(8).all()

    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, read=False
    ).count()

    return render_template(
        'main/dashboard.html',
        projects=projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        pending_tasks=pending_tasks,
        assigned_tasks=assigned_tasks[:5],
        due_soon_tasks=sorted(due_soon_tasks, key=lambda item: item.due_date)[:5],
        high_priority=high_priority,
        project_snapshots=project_snapshots,
        recent_tasks=sorted(all_tasks, key=lambda item: item.updated_at, reverse=True)[:8],
        workspace_activities=workspace_activities,
        unread_notifications=unread_notifications,
        completion_rate=round((completed_tasks / total_tasks * 100) if total_tasks else 0, 1),
    )
