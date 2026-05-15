from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    projects = current_user.projects
    all_tasks = [task for project in projects for task in project.tasks]
    total_tasks = len(all_tasks)
    completed_tasks = len([task for task in all_tasks if task.status == 'Done'])
    overdue_tasks = len([task for task in all_tasks if task.is_overdue])
    pending_tasks = len([task for task in all_tasks if task.status != 'Done'])

    return render_template(
        'main/dashboard.html',
        projects=projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        pending_tasks=pending_tasks,
        recent_tasks=sorted(all_tasks, key=lambda item: item.due_date or datetime.max)[:8],
    )