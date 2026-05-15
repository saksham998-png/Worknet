import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory
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
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(attachments_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # Compatibility aliases for legacy endpoint references
    app.add_url_rule('/', endpoint='home', view_func=app.view_functions['main.home'])
    app.add_url_rule('/dashboard', endpoint='dashboard', view_func=app.view_functions['main.dashboard'])
    app.add_url_rule('/signup', endpoint='signup', view_func=app.view_functions['auth.signup'])
    app.add_url_rule('/login', endpoint='login', view_func=app.view_functions['auth.login'])
    app.add_url_rule('/logout', endpoint='logout', view_func=app.view_functions['auth.logout'])
    app.add_url_rule('/projects/create', endpoint='create_project', view_func=app.view_functions['projects.create_project'])
    app.add_url_rule('/projects/<int:project_id>', endpoint='project_detail', view_func=app.view_functions['projects.project_detail'])
    app.add_url_rule('/projects/<int:project_id>/members/add', endpoint='add_project_member', view_func=app.view_functions['projects.add_project_member'])
    app.add_url_rule('/projects/<int:project_id>/tasks/create', endpoint='create_task', view_func=app.view_functions['tasks.create_task'])
    app.add_url_rule('/tasks/<int:task_id>/update-status', endpoint='update_task_status', view_func=app.view_functions['tasks.update_task_status'])
    app.add_url_rule('/tasks/<int:task_id>/update-priority', endpoint='update_task_priority', view_func=app.view_functions['tasks.update_task_priority'])
    app.add_url_rule('/tasks/<int:task_id>/comments', endpoint='add_comment', view_func=app.view_functions['comments.add_comment'])
    app.add_url_rule('/comments/<int:comment_id>/delete', endpoint='delete_comment', view_func=app.view_functions['comments.delete_comment'])
    app.add_url_rule('/tasks/<int:task_id>/attachments', endpoint='upload_attachment', view_func=app.view_functions['attachments.upload_attachment'])
    app.add_url_rule('/attachments/<int:attachment_id>/download', endpoint='download_attachment', view_func=app.view_functions['attachments.download_attachment'])
    app.add_url_rule('/attachments/<int:attachment_id>/delete', endpoint='delete_attachment', view_func=app.view_functions['attachments.delete_attachment'])

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

    @app.route('/favicon.ico')
    def favicon():
        # Serve the real favicon.svg for browser requests to /favicon.ico
        return send_from_directory(os.path.join(project_root, 'frontend', 'static'), 'favicon.svg', mimetype='image/svg+xml')

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
