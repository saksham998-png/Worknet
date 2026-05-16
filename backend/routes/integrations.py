from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, IntegrationConfig, ensure_user_workspace

integrations_bp = Blueprint('integrations', __name__)


@integrations_bp.route('/integrations')
@login_required
def settings():
    workspace = ensure_user_workspace(current_user)
    can_manage = workspace.can_manage(current_user)
    config = workspace.integrations
    if not config:
        config = IntegrationConfig(workspace=workspace)
        db.session.add(config)
        db.session.commit()
    return render_template(
        'integrations/settings.html',
        config=config,
        workspace=workspace,
        can_manage=can_manage,
    )


@integrations_bp.route('/integrations', methods=['POST'])
@login_required
def update_settings():
    workspace = ensure_user_workspace(current_user)
    if not workspace.can_manage(current_user):
        flash('Only workspace admins can change integration settings.', 'danger')
        return redirect(url_for('integrations.settings'))

    config = workspace.integrations
    if not config:
        config = IntegrationConfig(workspace=workspace)
        db.session.add(config)
    config.slack_webhook = request.form.get('slack_webhook', '').strip() or None
    config.teams_webhook = request.form.get('teams_webhook', '').strip() or None
    config.email_enabled = request.form.get('email_enabled') == 'on'
    db.session.commit()
    flash('Integration settings saved.', 'success')
    return redirect(url_for('integrations.settings'))
