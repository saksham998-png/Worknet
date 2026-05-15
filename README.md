# WorkNet

WorkNet is a full-stack team task management web application built with Flask. It helps teams manage projects, assign tasks, track progress, and collaborate through a clean dashboard with authentication and role-based access control.

## Project Structure

```text
worknet/
|-- frontend/                 # Frontend assets and templates
|   |-- static/               # CSS, JS, images
|   |   |-- css/
|   |   |-- js/
|   |   `-- images/
|   `-- templates/            # HTML templates organized by feature
|       |-- auth/
|       |-- main/
|       |-- projects/
|       |-- errors/
|       `-- layout.html
|-- backend/                  # Backend application code
|   |-- app.py                # Main Flask application
|   |-- config.py             # Application configuration
|   |-- models.py             # Database models
|   |-- routes/               # Route modules organized by feature
|   |-- utils/                # Utility functions
|   |-- uploads/              # File upload directory
|   |-- instance/             # Instance-specific configuration
|   |-- requirements.txt      # Python dependencies
|   |-- Procfile              # Deployment configuration
|   `-- README.md             # Backend-specific documentation
|-- .venv/                    # Python virtual environment
|-- run.py                    # Main entry point
|-- .gitignore
`-- README.md
```

## Features

- User authentication with signup and login
- Role-based access control for admins and members
- Project creation and team management
- Task creation, assignment, status tracking, and priorities
- Comments and file attachments on tasks
- Activity logging and REST API endpoints
- SQLite by default with configurable production database support

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies with `pip install -r backend/requirements.txt`.
4. Run the app with `python run.py`.
5. Open `http://localhost:5000`.

### Development Notes

- Frontend files live in `frontend/`.
- Backend logic lives in `backend/`.
- The application uses Flask blueprints for modular routing.
- SQLite is used for local development by default.

## Deployment

The application can be deployed to platforms like Railway, Heroku, AWS, or any server that supports Python and Flask.
