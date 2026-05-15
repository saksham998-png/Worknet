# WorkNet - Project Management Application

A modern, business-friendly project management application built with Flask.

## Project Structure

This project is organized into separate frontend and backend directories for better maintainability:

```
worknet/
├── frontend/                 # Frontend assets and templates
│   ├── static/              # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/           # HTML templates organized by feature
│       ├── auth/           # Authentication templates (login, signup)
│       ├── main/           # Main pages (home, dashboard)
│       ├── projects/       # Project-related templates
│       ├── errors/         # Error page templates
│       └── layout.html     # Base layout template
├── backend/                 # Backend application code
│   ├── app.py              # Main Flask application
│   ├── config.py           # Application configuration
│   ├── models.py           # Database models
│   ├── routes/             # Route modules organized by feature
│   │   ├── auth.py         # Authentication routes
│   │   ├── main.py         # Main application routes
│   │   ├── projects.py     # Project management routes
│   │   ├── tasks.py        # Task management routes
│   │   ├── comments.py     # Comment management routes
│   │   ├── attachments.py  # File attachment routes
│   │   └── api.py          # REST API endpoints
│   ├── utils/              # Utility functions
│   │   └── activity_logger.py
│   ├── uploads/            # File upload directory
│   ├── instance/           # Instance-specific configuration
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile            # Heroku deployment configuration
│   └── README.md           # Backend-specific documentation
├── .venv/                  # Python virtual environment
├── run.py                  # Main entry point
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Features

- **User Authentication**: Secure signup and login system
- **Project Management**: Create and manage projects with team members
- **Task Management**: Create, assign, and track tasks with priorities and due dates
- **Comments**: Add comments to tasks for collaboration
- **File Attachments**: Upload and manage files attached to tasks
- **Activity Logging**: Track all user actions and changes
- **REST API**: Programmatic access to projects, tasks, and activities
- **Business Theme**: Professional light theme suitable for business environments

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd worknet
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Development

- Frontend files (templates, CSS, JS) are in the `frontend/` directory
- Backend logic (routes, models, utilities) are in the `backend/` directory
- The application uses Flask blueprints for modular route organization
- Database: SQLite (development) / configurable for production

## Deployment

This application can be deployed to platforms like Heroku, AWS, or any server supporting Python/Flask applications.

## Contributing

1. Frontend changes: Modify files in `frontend/`
2. Backend changes: Modify files in `backend/`
3. Follow the existing code organization patterns
4. Test your changes thoroughly

## License

[Add your license information here]