from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.demo_data import seed_demo_for_user

help_bp = Blueprint('help', __name__)


@help_bp.route('/help')
def index():
    return render_template('help/index.html')


@help_bp.route('/help/demo-data', methods=['POST'])
@login_required
def load_demo():
    if seed_demo_for_user(current_user):
        flash('Demo data loaded successfully.', 'success')
    else:
        flash('Demo data already exists or could not be loaded.', 'warning')
    return redirect(url_for('main.dashboard'))
