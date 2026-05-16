from backend.models import db, Activity


def log_activity(user, action, description, project=None, task=None):
    workspace = None
    if project and project.workspace_id:
        workspace = project.workspace
    elif user.workspace_id:
        workspace = user.workspace

    activity = Activity(
        user=user,
        action=action,
        description=description,
        project=project,
        task=task,
        workspace_id=workspace.id if workspace else None,
    )
    db.session.add(activity)
    db.session.commit()
    return activity
