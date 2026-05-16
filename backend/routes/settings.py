from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models import db
from backend.utils.audit import log_audit

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def profile():
    return render_template('settings/profile.html')


@settings_bp.route('/settings', methods=['POST'])
@login_required
def update_profile():
    current_user.username = request.form.get('username', current_user.username).strip()
    current_user.bio = request.form.get('bio', '').strip() or None
    current_user.timezone = request.form.get('timezone', 'UTC').strip() or 'UTC'
    current_user.email_notifications = request.form.get('email_notifications') == 'on'
    dark_mode = request.form.get('dark_mode') == 'on'
    current_user.dark_mode = dark_mode
    db.session.commit()
    log_audit(current_user, 'profile_updated', 'Updated profile and preferences')
    flash('Settings saved.', 'success')
    return redirect(url_for('settings.profile'))


@settings_bp.route('/settings/theme', methods=['POST'])
@login_required
def toggle_theme():
    data = request.get_json(silent=True) or {}
    if 'dark_mode' in data:
        current_user.dark_mode = bool(data['dark_mode'])
    else:
        current_user.dark_mode = not current_user.dark_mode
    db.session.commit()
    return {'dark_mode': current_user.dark_mode}
