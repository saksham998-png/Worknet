import csv
import io
from datetime import datetime


def tasks_to_csv(tasks):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Due Date', 'Assignee', 'Project', 'Overdue'])
    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.status,
            task.priority,
            task.due_date.isoformat() if task.due_date else '',
            task.assignee.username if task.assignee else '',
            task.project.name,
            'Yes' if task.is_overdue else 'No',
        ])
    return output.getvalue()


def projects_report_csv(projects):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Project', 'Status', 'Total Tasks', 'Completed', 'In Progress', 'Overdue', 'Completion %'])
    for project in projects:
        stats = project.task_stats
        writer.writerow([
            project.name,
            project.status,
            stats['total'],
            stats['completed'],
            stats['in_progress'],
            stats['overdue'],
            round(stats['completion_rate'], 1),
        ])
    return output.getvalue()


def tasks_to_pdf_bytes(tasks, title='WorkNet Report'):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont('Helvetica-Bold', 16)
        c.drawString(50, y, title)
        y -= 30
        c.setFont('Helvetica', 10)
        c.drawString(50, y, f'Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}')
        y -= 30
        for task in tasks[:80]:
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont('Helvetica', 10)
            line = f'[{task.status}] {task.title} — {task.project.name}'
            c.drawString(50, y, line[:95])
            y -= 16
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        content = f'{title}\nGenerated {datetime.utcnow()}\n\n'
        for task in tasks:
            content += f'- [{task.status}] {task.title} ({task.project.name})\n'
        return content.encode('utf-8')
