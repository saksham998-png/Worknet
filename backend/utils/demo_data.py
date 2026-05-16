from datetime import datetime, timedelta
from models import (
    db, User, Project, Task, Membership, Comment, Activity,
    create_workspace_for_user,
)
from utils.activity_logger import log_activity


def seed_demo_for_user(user):
    if Project.query.filter_by(owner_id=user.id).count() > 0:
        return False

    if not user.workspace_id:
        create_workspace_for_user(user, name=f'{user.username} Team')

    workspace = user.workspace
    projects_data = [
        {
            'name': 'Product Launch',
            'description': 'Q2 launch planning and execution',
            'color': '#1c8b7c',
            'tasks': [
                ('Finalize landing page copy', 'In Progress', 'High', 2),
                ('Review analytics dashboard', 'To Do', 'Medium', 5),
                ('Ship beta to early adopters', 'To Do', 'Urgent', 7),
                ('Post-launch retrospective', 'To Do', 'Low', 14),
            ],
        },
        {
            'name': 'Client Onboarding',
            'description': 'Streamline new customer setup',
            'color': '#f08a5d',
            'tasks': [
                ('Create welcome email sequence', 'Done', 'Medium', -3),
                ('Build onboarding checklist template', 'In Progress', 'High', 1),
                ('Schedule kickoff calls', 'To Do', 'Medium', 4),
            ],
        },
    ]

    for pdata in projects_data:
        project = Project(
            name=pdata['name'],
            description=pdata['description'],
            owner=user,
            workspace=workspace,
            color=pdata['color'],
        )
        db.session.add(project)
        db.session.flush()
        db.session.add(Membership(user=user, project=project, role='Admin'))

        for idx, (title, status, priority, days_offset) in enumerate(pdata['tasks']):
            task = Task(
                title=title,
                description=f'Demo task for {pdata["name"]}.',
                status=status,
                priority=priority,
                due_date=(datetime.utcnow() + timedelta(days=days_offset)).date(),
                project=project,
                creator=user,
                assignee=user,
                sort_order=idx,
            )
            db.session.add(task)
            db.session.flush()
            log_activity(user, 'created_task', f'Created task "{title}"', project=project, task=task)

        if project.tasks:
            db.session.add(Comment(
                content=f'Welcome to {pdata["name"]}! @{user.username} — demo data loaded.',
                task=project.tasks[0],
                author=user,
            ))

    user.onboarding_completed = True
    db.session.commit()
    return True
