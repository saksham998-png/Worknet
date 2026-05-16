from flask import Blueprint, render_template, Response, request
from flask_login import login_required, current_user
from backend.models import Project, Task
from backend.utils.export import tasks_to_csv, projects_report_csv, tasks_to_pdf_bytes

reports_bp = Blueprint('reports', __name__)


def _user_tasks():
    projects = current_user.projects
    return [task for project in projects for task in project.tasks]


@reports_bp.route('/reports')
@login_required
def dashboard():
    projects = current_user.projects
    all_tasks = _user_tasks()
    status_counts = {'To Do': 0, 'In Progress': 0, 'Done': 0}
    priority_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Urgent': 0}
    for task in all_tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1

    project_health = [
        {
            'name': p.name,
            'completion': round(p.task_stats['completion_rate'], 1),
            'overdue': p.task_stats['overdue'],
            'total': p.task_stats['total'],
            'color': p.color,
        }
        for p in projects
    ]

    return render_template(
        'reports/dashboard.html',
        projects=projects,
        status_counts=status_counts,
        priority_counts=priority_counts,
        project_health=project_health,
        total_tasks=len(all_tasks),
        completed=len([t for t in all_tasks if t.status == 'Done']),
    )


@reports_bp.route('/reports/export/csv')
@login_required
def export_csv():
    scope = request.args.get('scope', 'tasks')
    if scope == 'projects':
        content = projects_report_csv(current_user.projects)
        filename = 'worknet-projects.csv'
    else:
        content = tasks_to_csv(_user_tasks())
        filename = 'worknet-tasks.csv'
    return Response(
        content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


@reports_bp.route('/reports/export/pdf')
@login_required
def export_pdf():
    tasks = _user_tasks()
    pdf_bytes = tasks_to_pdf_bytes(tasks, title='WorkNet Task Report')
    mimetype = 'application/pdf' if pdf_bytes[:4] == b'%PDF' else 'text/plain'
    ext = 'pdf' if mimetype == 'application/pdf' else 'txt'
    return Response(
        pdf_bytes,
        mimetype=mimetype,
        headers={'Content-Disposition': f'attachment; filename=worknet-report.{ext}'},
    )
