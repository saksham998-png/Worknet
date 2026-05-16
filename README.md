# WorkNet

WorkNet is a polished team workspace built with Flask, designed to help teams organize projects, assign work, and track progress with a clean, professional interface.

## Key Features

- Secure authentication with signup and login
- Role-based access control for admins and members
- Project creation, team collaboration, and membership management
- Task creation, assignment, priority, and status tracking
- Comments and file attachments for task-level collaboration
- Workspace dashboard with progress summaries and activity insights
- REST-style API support for integrations and automation

## Technology Stack

- Python / Flask
- SQLAlchemy ORM
- Flask-Login authentication
- Jinja2 templating
- Bootstrap 5 and custom UI styles
- SQLite for local development (configurable for production databases)

## Repository Structure

```text
worknet/
├── frontend/               # Frontend templates and static assets
│   ├── static/             # CSS, JavaScript, favicon and media
│   └── templates/          # Jinja2 templates by feature
├── backend/                # Flask application and backend logic
│   ├── routes/             # Feature-based route modules
│   ├── models.py           # Database models and relationships
│   ├── config.py           # Environment and app configuration
│   └── app.py              # Flask application factory and bootstrap
├── app.py                  # Top-level entry point for the repository
├── README.md               # Project overview and setup guide
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.8 or newer
- `pip`

### Local Setup

```bash
git clone https://github.com/saksham998-png/Worknet.git
cd Worknet
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Development Workflow

- Frontend structure: `frontend/static/` and `frontend/templates/`
- Backend structure: `backend/app.py`, `backend/routes/`, `backend/models.py`
- Flask blueprints are used to keep routes modular and maintainable
- Static assets are served from `frontend/static`
- Templates are served from `frontend/templates`

## Deployment Notes

WorkNet is ready to deploy on any platform that supports Python and Flask. Recommended steps:

1. Configure production database credentials in `backend/config.py`
2. Set `FLASK_ENV=production` and `FLASK_DEBUG=0`
3. Use a production WSGI server such as Gunicorn or uWSGI
4. Ensure static assets are accessible via the configured static folder

## Contribution

Contributions are welcome. If you want to extend the app or improve the UI:

- Create a new branch for your feature
- Add tests where possible
- Keep code modular and consistent with existing structure
- Open a pull request with a summary of your changes

## License

This repository is published under the MIT License.
