from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role = db.Column(db.String(20), default='Member', nullable=False)

    user = db.relationship('User', back_populates='memberships')
    project = db.relationship('Project', back_populates='memberships')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'project_id', name='uix_user_project'),
    )

    def __repr__(self):
        return f'<Membership {self.user_id} in {self.project_id}: {self.role}>'

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

    memberships = db.relationship('Membership', back_populates='user', cascade='all, delete-orphan')
    owned_projects = db.relationship('Project', back_populates='owner', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Task', back_populates='assignee', foreign_keys='Task.assignee_id')
    created_tasks = db.relationship('Task', back_populates='creator', foreign_keys='Task.creator_id')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='user', cascade='all, delete-orphan')

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='Active', nullable=False)
    color = db.Column(db.String(7), default='#1a73e8', nullable=False)  # Hex color

    owner = db.relationship('User', back_populates='owned_projects')
    memberships = db.relationship('Membership', back_populates='project', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='project', cascade='all, delete-orphan')
    activities = db.relationship('Activity', back_populates='project', cascade='all, delete-orphan')

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
            'completion_rate': (completed / total * 100) if total > 0 else 0
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
        }

    def __repr__(self):
        return f'<Project {self.name}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='To Do', nullable=False)
    priority = db.Column(db.String(20), default='Medium', nullable=False)
    due_date = db.Column(db.Date, nullable=True)
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
            'Urgent': '#ef4444'
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
            'creator_email': self.creator.email if self.creator else None,
            'is_overdue': self.is_overdue,
            'comment_count': len(self.comments),
            'attachment_count': len(self.attachments),
        }

    def __repr__(self):
        return f'<Task {self.title}>'

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

    def __repr__(self):
        return f'<Comment by {self.author.username} on task {self.task.title}>'

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

    def __repr__(self):
        return f'<Attachment {self.filename}>'

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # created, updated, commented, etc.
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)

    user = db.relationship('User', back_populates='activities')
    project = db.relationship('Project', back_populates='activities')
    task = db.relationship('Task', back_populates='activities')

    def __repr__(self):
        return f'<Activity {self.action} by {self.user.username}>'