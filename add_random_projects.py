import os
import sys
import random
from datetime import datetime, timedelta

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, User, Workspace, Project, Membership, WorkspaceMember, Task

app = create_app()

PROJECT_NAMES = [
    "Website Redesign", "Mobile App v2", "Marketing Campaign",
    "Security Audit", "Cloud Migration", "Customer Portal"
]

TASK_TITLES = [
    "Design Mockups", "Write API Docs", "Setup CI/CD",
    "Fix CSS bugs", "Run Performance Tests", "Final Review"
]

with app.app_context():
    # 1. Ensure all dummy users are Workspace Members
    main_workspace = Workspace.query.first()
    if not main_workspace:
        print("No workspace found.")
        sys.exit(1)
        
    dummy_users = User.query.filter(User.email.like('%@example.com')).all()
    for user in dummy_users:
        # Link to workspace
        user.workspace_id = main_workspace.id
        # Ensure WorkspaceMember entry
        wm = WorkspaceMember.query.filter_by(workspace_id=main_workspace.id, user_id=user.id).first()
        if not wm:
            db.session.add(WorkspaceMember(workspace_id=main_workspace.id, user_id=user.id, role='Member'))
    
    db.session.commit()
    print(f"Ensured {len(dummy_users)} users are workspace members.")

    # 2. Add some random projects
    main_user = User.query.filter_by(username='saksham').first() or User.query.first()
    
    for p_name in PROJECT_NAMES:
        # Check if project exists
        proj = Project.query.filter_by(name=p_name).first()
        if not proj:
            proj = Project(
                name=p_name,
                description=f"Automated demo project for {p_name}.",
                owner=main_user,
                workspace=main_workspace,
                status=random.choice(['Active', 'Active', 'Active', 'Paused', 'Archived'])
            )
            db.session.add(proj)
            db.session.flush()
            
            # Add some members to the project
            members_to_add = random.sample(dummy_users, k=min(4, len(dummy_users)))
            # Add owner
            db.session.add(Membership(user=main_user, project=proj, role='Admin'))
            
            for m in members_to_add:
                db.session.add(Membership(user=m, project=proj, role='Member'))
            
            # Add some tasks
            for i, t_title in enumerate(TASK_TITLES):
                task = Task(
                    title=t_title,
                    description=f"Task for {p_name}",
                    status=random.choice(['To Do', 'In Progress', 'Done']),
                    priority=random.choice(['Low', 'Medium', 'High', 'Urgent']),
                    due_date=(datetime.utcnow() + timedelta(days=random.randint(1, 14))).date(),
                    project=proj,
                    creator=main_user,
                    assignee=random.choice(members_to_add + [main_user]),
                    sort_order=i
                )
                db.session.add(task)
            
            print(f"Created project: {p_name}")
    
    db.session.commit()

print("Demo data generation complete!")
