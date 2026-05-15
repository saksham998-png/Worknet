import os
from datetime import datetime
from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from config import Config


def _is_debug_enabled():
    return os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}


def create_app():
    # Get the project root directory (parent of backend folder)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(__name__,
                instance_relative_config=True,
                template_folder=os.path.join(project_root, 'frontend', 'templates'),
                static_folder=os.path.join(project_root, 'frontend', 'static'))
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Config.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to continue.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.comments import comments_bp
    from routes.attachments import attachments_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(attachments_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Create database tables
    with app.app_context():
        db.create_all()

    # Error handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    debug = _is_debug_enabled()
    app.run(
        debug=debug,
        use_reloader=debug,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
    )
