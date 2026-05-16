"""Lightweight SQLite migrations for new columns on existing installs."""
from sqlalchemy import inspect, text


def run_migrations(db):
    engine = db.engine
    inspector = inspect(engine)

    user_columns = {c['name'] for c in inspector.get_columns('users')} if inspector.has_table('users') else set()
    user_additions = {
        'workspace_id': 'INTEGER',
        'onboarding_completed': 'BOOLEAN DEFAULT 0',
        'dark_mode': 'BOOLEAN DEFAULT 0',
        'email_notifications': 'BOOLEAN DEFAULT 1',
        'timezone': "VARCHAR(50) DEFAULT 'UTC'",
        'is_active': 'BOOLEAN DEFAULT 1',
    }
    for col, col_type in user_additions.items():
        if col not in user_columns and inspector.has_table('users'):
            db.session.execute(text(f'ALTER TABLE users ADD COLUMN {col} {col_type}'))
            db.session.commit()

    if inspector.has_table('projects'):
        project_columns = {c['name'] for c in inspector.get_columns('projects')}
        if 'workspace_id' not in project_columns:
            db.session.execute(text('ALTER TABLE projects ADD COLUMN workspace_id INTEGER'))
            db.session.commit()

    if inspector.has_table('tasks'):
        task_columns = {c['name'] for c in inspector.get_columns('tasks')}
        if 'sort_order' not in task_columns:
            db.session.execute(text('ALTER TABLE tasks ADD COLUMN sort_order INTEGER DEFAULT 0'))
            db.session.commit()

    if inspector.has_table('activities'):
        activity_columns = {c['name'] for c in inspector.get_columns('activities')}
        if 'workspace_id' not in activity_columns:
            db.session.execute(text('ALTER TABLE activities ADD COLUMN workspace_id INTEGER'))
            db.session.commit()
