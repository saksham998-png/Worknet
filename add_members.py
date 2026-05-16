import os
import sys
import random

# Add backend directory to Python path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, User, Workspace, Project, Membership

app = create_app()

NAMES = [
    "Alex Johnson", "Sam Taylor", "Jordan Lee", "Casey Smith",
    "Taylor Davis", "Morgan White", "Riley Brown", "Quinn Miller",
    "Avery Wilson", "Devon Moore", "Skyler Anderson", "Jesse Thomas"
]

with app.app_context():
    # Find the main workspace and projects
    main_workspace = Workspace.query.first()
    projects = Project.query.all()
    
    if not projects:
        print("No projects found to add members to.")
        sys.exit(1)

    for name in NAMES:
        first, last = name.split()
        email = f"{first.lower()}.{last.lower()}@example.com"
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(
                username=name,
                email=email,
                password_hash=generate_password_hash("password123"),
                onboarding_completed=True
            )
            if main_workspace:
                user.workspace_id = main_workspace.id
            db.session.add(user)
            db.session.commit()
            
            # Add to all projects as member
            for proj in projects:
                mem = Membership.query.filter_by(user_id=user.id, project_id=proj.id).first()
                if not mem:
                    new_mem = Membership(user=user, project=proj, role='Member')
                    db.session.add(new_mem)
            db.session.commit()
            print(f"Added user {name}")
        else:
            print(f"User {name} already exists")

print("Done adding members!")
