from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from backend.models import db, Workspace, WorkspaceMember, WorkspaceInvite, create_invite, ensure_user_workspace
from backend.utils.audit import log_audit

workspace_bp = Blueprint('workspace', __name__)


@workspace_bp.route('/workspace')
@login_required
def settings():
    workspace = ensure_user_workspace(current_user)
    can_manage = workspace.can_manage(current_user)
    invites = []
    if can_manage:
        invites = WorkspaceInvite.query.filter_by(workspace_id=workspace.id).order_by(
            WorkspaceInvite.created_at.desc()
        ).limit(10).all()
    members = WorkspaceMember.query.filter_by(workspace_id=workspace.id).all()
    return render_template(
        'workspace/settings.html',
        workspace=workspace,
        invites=invites,
        members=members,
        can_manage=can_manage,
    )


@workspace_bp.route('/workspace/invite', methods=['POST'])
@login_required
def create_invite_link():
    workspace = ensure_user_workspace(current_user)
    if not workspace.can_manage(current_user):
        flash('Only workspace admins can create invite links.', 'danger')
        return redirect(url_for('workspace.settings'))

    role = request.form.get('role', 'Member')
    days = min(int(request.form.get('days', 7) or 7), 30)
    invite = create_invite(workspace, current_user, role=role, days=days)
    db.session.commit()
    log_audit(current_user, 'invite_created', f'Created invite link for role {role}', workspace)
    flash('Invite link created.', 'success')
    return redirect(url_for('workspace.settings'))


@workspace_bp.route('/join/<token>')
def join_workspace(token):
    invite = WorkspaceInvite.query.filter_by(token=token).first_or_404()
    if not invite.is_valid:
        flash('This invite link has expired or was already used.', 'danger')
        return redirect(url_for('auth.login'))

    if not current_user.is_authenticated:
        flash('Sign in or create an account to join the workspace.', 'info')
        return redirect(url_for('auth.login', next=request.url))

    existing = WorkspaceMember.query.filter_by(
        workspace_id=invite.workspace_id, user_id=current_user.id
    ).first()
    if not existing:
        db.session.add(WorkspaceMember(
            workspace_id=invite.workspace_id,
            user_id=current_user.id,
            role=invite.role,
        ))
    invite.used_at = datetime.utcnow()
    invite.used_by_id = current_user.id
    current_user.workspace_id = invite.workspace_id
    db.session.commit()
    log_audit(current_user, 'invite_accepted', 'Joined workspace via invite', invite.workspace)
    flash(f'Welcome to {invite.workspace.name}!', 'success')
    return redirect(url_for('main.dashboard'))
