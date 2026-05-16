from backend.app import create_app
from backend.models import db, Project

app = create_app()
with app.app_context():
    # Update all projects with status 'Open' to 'Active'
    updated = Project.query.filter_by(status='Open').update({Project.status: 'Active'})
    db.session.commit()
    print(f"Updated {updated} projects from 'Open' to 'Active'.")
