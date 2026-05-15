from models import db, Activity

def log_activity(user, action, description, project=None, task=None):
    """Helper function to log user activities"""
    activity = Activity(
        user=user,
        action=action,
        description=description,
        project=project,
        task=task
    )
    db.session.add(activity)
    db.session.commit()