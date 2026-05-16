import json
import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Workspace(db.Model):
    __tablename__ = 'workspaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', back_populates='owned_workspaces', foreign_keys=[owner_id])
    members = db.relationship('WorkspaceMember', back_populates='workspace', cascade='all, delete-orphan')
    projects = db.relationship('Project', back_populates='workspace', cascade='all, delete-orphan')
    invites = db.relationship('WorkspaceInvite', back_populates='workspace', cascade='all, delete-orphan')
    integrations = db.relationship('IntegrationConfig', back_populates='workspace', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='workspace', cascade='all, delete-orphan')

    def member_users(self):
        return [m.user for m in self.members]

    def can_manage(self, user):
        if user.id == self.owner_id:
            return True
        membership = next((m for m in self.members if m.user_id == user.id), None)
        return membership and membership.role == 'Admin'


class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='Member', nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    workspace = db.relationship('Workspace', back_populates='members')
    user = db.relationship('User', back_populates='workspace_memberships')

    __table_args__ = (db.UniqueConstraint('workspace_id', 'user_id', name='uix_workspace_user'),)


class WorkspaceInvite(db.Model):
    __tablename__ = 'workspace_invites'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), default='Member', nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    used_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workspace = db.relationship('Workspace', back_populates='invites')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    used_by = db.relationship('User', foreign_keys=[used_by_id])

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > datetime.utcnow()


class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role = db.Column(db.String(20), default='Member', nullable=False)

    user = db.relationship('User', back_populates='memberships')
    project = db.relationship('Project', back_populates='memberships')

    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='uix_user_project'),)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Member', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    timezone = db.Column(db.String(50), default='UTC', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    workspace = db.relationship('Workspace', foreign_keys=[workspace_id])
    owned_workspaces = db.relationship('Workspace', back_populates='owner', foreign_keys='Workspace.owner_id')
    workspace_memberships = db.relationship('WorkspaceMember', back_populates='user', cascade='all, delete-orphan')
    memberships = db.relationship('Membership', back_populates='user', cascade='all, delete-orphan')
    owned_projects = db.relationship('Project', back_populates='owner', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Task', back_populates='assignee', foreign_keys='Task.assignee_id')
    created_tasks = db.relationship('Task', back_populates='creator', foreign_keys='Task.creator_id')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='user', cascade='all, delete-orphan')
    saved_views = db.relationship('SavedView', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    mentions_received = db.relationship('Mention', back_populates='mentioned_user', cascade='all, delete-orphan')

    @property
    def projects(self):
        items = {membership.project for membership in self.memberships}
        items.update(self.owned_projects)
        return sorted(items, key=lambda project: project.created_at, reverse=True)

    def __repr__(self):
        return f'<User {self.email}>'


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='Active', nullable=False)
    color = db.Column(db.String(7), default='#1a73e8', nullable=False)

    owner = db.relationship('User', back_populates='owned_projects')
    workspace = db.relationship('Workspace', back_populates='projects')
    memberships = db.relationship('Membership', back_populates='project', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='project', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='project', cascade='all, delete-orphan')
    saved_views = db.relationship('SavedView', back_populates='project', cascade='all, delete-orphan')

    @property
    def members(self):
        return [membership.user for membership in self.memberships]

    @property
    def task_stats(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == 'Done'])
        in_progress = len([t for t in self.tasks if t.status == 'In Progress'])
        overdue = len([t for t in self.tasks if t.is_overdue])
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'overdue': overdue,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
        }

    def member_role(self, user):
        if user == self.owner:
            return 'Admin'
        membership = next((m for m in self.memberships if m.user_id == user.id), None)
        return membership.role if membership else None

    def can_manage(self, user):
        return user == self.owner or self.member_role(user) == 'Admin'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner.username,
            'owner_email': self.owner.email,
            'members': [member.email for member in self.members],
            'created_at': self.created_at.isoformat(),
            'task_count': len(self.tasks),
            'status': self.status,
            'color': self.color,
            'health': self.task_stats,
        }


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='To Do', nullable=False)
    priority = db.Column(db.String(20), default='Medium', nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    project = db.relationship('Project', back_populates='tasks')
    assignee = db.relationship('User', back_populates='assigned_tasks', foreign_keys=[assignee_id])
    creator = db.relationship('User', back_populates='created_tasks', foreign_keys=[creator_id])
    comments = db.relationship('Comment', back_populates='task', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', back_populates='task', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='task', cascade='all, delete-orphan')

    @property
    def is_overdue(self):
        return self.due_date is not None and self.due_date < datetime.utcnow().date() and self.status != 'Done'

    @property
    def priority_color(self):
        return {
            'Low': '#64748b',
            'Medium': '#f59e0b',
            'High': '#ec4899',
            'Urgent': '#ef4444',
        }.get(self.priority, '#64748b')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'project_id': self.project_id,
            'assignee_email': self.assignee.email if self.assignee else None,
            'assignee_username': self.assignee.username if self.assignee else None,
            'creator_email': self.creator.email if self.creator else None,
            'is_overdue': self.is_overdue,
            'sort_order': self.sort_order,
            'comment_count': len(self.comments),
            'attachment_count': len(self.attachments),
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    task = db.relationship('Task', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    mentions = db.relationship('Mention', back_populates='comment', cascade='all, delete-orphan')


class Mention(db.Model):
    __tablename__ = 'mentions'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comment = db.relationship('Comment', back_populates='mentions')
    mentioned_user = db.relationship('User', back_populates='mentions_received')


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    task = db.relationship('Task', back_populates='attachments')
    uploader = db.relationship('User', foreign_keys=[uploader_id])


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)

    user = db.relationship('User', back_populates='activities')
    project = db.relationship('Project', back_populates='activities')
    task = db.relationship('Task', back_populates='activities')


class SavedView(db.Model):
    __tablename__ = 'saved_views'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filters_json = db.Column(db.Text, nullable=False, default='{}')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='saved_views')
    project = db.relationship('Project', back_populates='saved_views')

    @property
    def filters(self):
        try:
            return json.loads(self.filters_json or '{}')
        except json.JSONDecodeError:
            return {}

    @filters.setter
    def filters(self, value):
        self.filters_json = json.dumps(value or {})


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=True)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')


class IntegrationConfig(db.Model):
    __tablename__ = 'integration_configs'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), unique=True, nullable=False)
    slack_webhook = db.Column(db.String(500), nullable=True)
    teams_webhook = db.Column(db.String(500), nullable=True)
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)

    workspace = db.relationship('Workspace', back_populates='integrations')


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workspace = db.relationship('Workspace', back_populates='audit_logs')
    user = db.relationship('User', foreign_keys=[user_id])


def create_workspace_for_user(user, name=None):
    base_name = name or f"{user.username}'s Workspace"
    slug_base = ''.join(c for c in user.username.lower() if c.isalnum()) or 'workspace'
    slug = f"{slug_base}-{user.id}"
    workspace = Workspace(name=base_name, slug=slug, owner_id=user.id)
    db.session.add(workspace)
    db.session.flush()
    db.session.add(WorkspaceMember(workspace=workspace, user=user, role='Admin'))
    db.session.add(IntegrationConfig(workspace=workspace))
    user.workspace_id = workspace.id
    return workspace


def ensure_user_workspace(user):
    """Create or repair workspace membership for legacy accounts."""
    if not user.workspace_id:
        ws = create_workspace_for_user(user)
        db.session.commit()
        return ws

    workspace = Workspace.query.get(user.workspace_id)
    if workspace is None:
        ws = create_workspace_for_user(user)
        db.session.commit()
        return ws

    membership = WorkspaceMember.query.filter_by(
        workspace_id=workspace.id, user_id=user.id
    ).first()
    if membership is None:
        role = 'Admin' if workspace.owner_id == user.id else 'Member'
        db.session.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role=role))

    if workspace.integrations is None:
        db.session.add(IntegrationConfig(workspace=workspace))

    if workspace.owner_id == user.id:
        user.workspace_id = workspace.id

    db.session.commit()
    return workspace


def create_invite(workspace, created_by, role='Member', days=7):
    invite = WorkspaceInvite(
        workspace=workspace,
        token=WorkspaceInvite.generate_token(),
        role=role,
        created_by_id=created_by.id,
        expires_at=datetime.utcnow() + timedelta(days=days),
    )
    db.session.add(invite)
    return invite
