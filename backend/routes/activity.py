from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Activity, Mention

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/activity')
@login_required
def feed():
    workspace_id = current_user.workspace_id
    query = Activity.query
    if workspace_id:
        query = query.filter(
            (Activity.workspace_id == workspace_id) | (Activity.user_id == current_user.id)
        )
    else:
        query = query.filter_by(user_id=current_user.id)
    activities = query.order_by(Activity.created_at.desc()).limit(100).all()
    mentions = Mention.query.filter_by(mentioned_user_id=current_user.id).order_by(
        Mention.created_at.desc()
    ).limit(20).all()
    return render_template('activity/feed.html', activities=activities, mentions=mentions)
