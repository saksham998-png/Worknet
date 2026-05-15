# WorkNet

A Flask-based team task manager built for production deployment. Users can sign up, log in, create projects, assign tasks, invite teammates, and track project progress with role-based access.

## Features

- Signup / Login with secure password hashing
- Role-based access control (Admin / Member)
- Project creation and team management
- Task creation, assignment, status tracking, and overdue detection
- REST API endpoints for projects and tasks
- SQLite by default, configurable with `DATABASE_URL`
- Deployable on Railway with Gunicorn

## Run locally

1. Open PowerShell in the project root:

```powershell
cd C:\ethara_website_project
```

2. Activate the virtual environment:

```powershell
.\.venv\Script\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Start the app:

```powershell
python app.py
```

5. Open http://127.0.0.1:5000

## Deployment

Railway can deploy this app directly from your GitHub repository.

- Ensure `Procfile` contains:

```text
web: gunicorn app:app
```

- Set `SECRET_KEY` and `DATABASE_URL` as environment variables in Railway.

## API Endpoints

- `GET /api/projects` - list current user projects
- `GET /api/projects/<project_id>/tasks` - list tasks for a project
- `PATCH /api/tasks/<task_id>` - update task status

## Notes

- The first registered user becomes an Admin.
- New users are Members by default.
- Project owners and project Admin members can manage tasks and invite teammates.
