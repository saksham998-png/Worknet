import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, current_user
from backend.models import db, User
from backend.config import Config


def _is_debug_enabled():
    return os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}


def create_app():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(project_root, 'frontend', 'templates'),
        static_folder=os.path.join(project_root, 'frontend', 'static'),
    )
    app.config.from_object(Config)
    print(f"DEBUG: Template folder: {app.template_folder}")
    print(f"DEBUG: Static folder: {app.static_folder}")

    print("DEBUG: Initializing database...")
    db.init_app(app)
    Config.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to continue.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from backend.routes.auth import auth_bp
    from backend.routes.main import main_bp
    from backend.routes.projects import projects_bp
    from backend.routes.tasks import tasks_bp
    from backend.routes.comments import comments_bp
    from backend.routes.attachments import attachments_bp
    from backend.routes.api import api_bp
    from backend.routes.admin import admin_bp
    from backend.routes.onboarding import onboarding_bp
    from backend.routes.settings import settings_bp
    from backend.routes.workspace import workspace_bp
    from backend.routes.views import views_bp
    from backend.routes.reports import reports_bp
    from backend.routes.help import help_bp
    from backend.routes.integrations import integrations_bp
    from backend.routes.activity import activity_bp

    for bp in (
        auth_bp, main_bp, projects_bp, tasks_bp, comments_bp, attachments_bp,
        api_bp, admin_bp, onboarding_bp, settings_bp, workspace_bp, views_bp,
        reports_bp, help_bp, integrations_bp, activity_bp,
    ):
        app.register_blueprint(bp)

    from backend.utils.socketio_events import init_socketio
    app.socketio = init_socketio(app)

    # Routes are registered via Blueprints above


    @app.context_processor
    def inject_globals():
        dark = False
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            dark = current_user.dark_mode
        return {'now': datetime.utcnow(), 'dark_mode': dark}

    with app.app_context():
        try:
            print("DEBUG: Running database setup and migrations...")
            db.create_all()
            from backend.utils.db_migrate import run_migrations
            run_migrations(db)
            print("DEBUG: Database setup complete.")
        except Exception as e:
            print(f"WARNING: Database setup failed or timed out: {e}")
            print("The app will attempt to continue starting...")

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(project_root, 'frontend', 'static'),
            'favicon.svg',
            mimetype='image/svg+xml',
        )

    return app


# App instance is created by the factory function in Procfile or main block below


if __name__ == '__main__':
    app = create_app()
    debug = _is_debug_enabled()
    app.socketio.run(
        app,
        debug=debug,
        use_reloader=debug,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        allow_unsafe_werkzeug=True,
    )
