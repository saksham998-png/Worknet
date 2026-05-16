from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, create_workspace_for_user
from utils.demo_data import seed_demo_for_user
from utils.audit import log_audit

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('main.dashboard'))

    step = request.args.get('step', '1')
    if request.method == 'POST':
        action = request.form.get('action', 'next')
        if action == 'skip':
            current_user.onboarding_completed = True
            db.session.commit()
            flash('Onboarding skipped. You can load demo data anytime from Help.', 'info')
            return redirect(url_for('main.dashboard'))

        if step == '1':
            workspace_name = request.form.get('workspace_name', '').strip()
            if not current_user.workspace_id:
                create_workspace_for_user(current_user, name=workspace_name or None)
            elif workspace_name and current_user.workspace:
                current_user.workspace.name = workspace_name
            db.session.commit()
            return redirect(url_for('onboarding.onboarding', step='2'))

        if step == '2':
            team_size = request.form.get('team_size', 'solo')
            use_case = request.form.get('use_case', 'projects')
            flash(f'Workspace tuned for {team_size} teams focused on {use_case}.', 'success')
            return redirect(url_for('onboarding.onboarding', step='3'))

        if step == '3':
            if request.form.get('load_demo') == 'yes':
                seed_demo_for_user(current_user)
                flash('Demo projects and tasks loaded.', 'success')
            current_user.onboarding_completed = True
            db.session.commit()
            log_audit(current_user, 'onboarding_complete', 'User completed onboarding flow')
            flash('You are all set. Welcome to WorkNet!', 'success')
            return redirect(url_for('main.dashboard'))

    return render_template('onboarding/wizard.html', step=step)
