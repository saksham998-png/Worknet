# WorkNet

<div align="center">
  <h3>A calm, clear, and powerful team workspace built with Python and Flask.</h3>
</div>

## 🚀 Overview

WorkNet is a polished, production-ready workspace designed to help teams organize projects, assign work, and track progress effortlessly. Built with a focus on modern aesthetics and real-time collaboration, WorkNet provides a clean, professional interface that scales with your team's needs.

## ✨ Key Features

- **Real-Time Collaboration**: Powered by WebSockets, get instant updates on task changes and activity without refreshing the page.
- **Dynamic Theming System**: Four full-fledged design systems to customize your workspace experience:
  - ☀️ **Light (Default)**: Clean, calm, and professional typography.
  - 🌙 **Dark**: Sleek, high-tech, and stealthy interface.
  - 🌊 **Ocean**: Fluid and friendly with modern Glassmorphism.
  - 🌅 **Sunset**: Bold and retro with a striking Neo-brutalist aesthetic.
- **Advanced Task Management**: Create, assign, prioritize, and track tasks. Includes interactive Kanban boards with drag-and-drop functionality.
- **Project & Team Organization**: Create distinct projects, manage workspaces, and control access with role-based permissions (Admin/Member).
- **Insights & Reporting**: Visual dashboards using Chart.js to monitor project health, task priority distribution, and completion rates.
- **Activity & Auditing**: Comprehensive activity feeds and system audit logs for accountability and transparency.
- **Secure Authentication**: Built-in signup, login, and session management using Flask-Login.

## 🛠️ Technology Stack

**Backend**
- **Framework**: Python / Flask
- **Database**: SQLite (Configurable to PostgreSQL/MySQL via SQLAlchemy)
- **ORM**: Flask-SQLAlchemy
- **Real-time**: Flask-SocketIO
- **Security**: Flask-Login, Werkzeug Security

**Frontend**
- **Structure & Logic**: HTML5, Vanilla JavaScript
- **Styling**: Vanilla CSS (CSS Variables) & Bootstrap 5
- **Interactive UI**: SortableJS (Kanban drag-and-drop), Chart.js (Data visualization)
- **Icons**: FontAwesome

## 📂 Repository Structure

```text
Worknet/
├── backend/                # Flask application logic, database models, and API endpoints
│   ├── routes/             # Modular feature routes (auth, projects, tasks, etc.)
│   ├── utils/              # Helper functions (sockets, notifications, audit logs)
│   ├── models.py           # Database schema definition
│   ├── config.py           # Environment and app configuration
│   └── app.py              # Flask app factory initialization
├── frontend/               # Frontend presentation layer
│   ├── static/             # Vanilla CSS, JS, and assets (themes located in features.css)
│   └── templates/          # Jinja2 HTML templates organized by feature
├── instance/               # Local SQLite database files (ignored in git)
├── app.py                  # Top-level entry point to run the server
├── README.md               # You are here!
└── .gitignore
```

## 💻 Getting Started

### Prerequisites
- Python 3.8 or higher
- `pip` package manager

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/saksham998-png/Worknet.git
   cd Worknet
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python app.py
   ```

5. **Open your browser:** Navigate to `http://127.0.0.1:5000` to see WorkNet in action!

## 🚢 Deployment

WorkNet is ready for deployment on any standard Python hosting environment (Heroku, Render, AWS, DigitalOcean). 

1. Update `backend/config.py` with your production database URI.
2. Set environment variables `FLASK_ENV=production` and `FLASK_DEBUG=0`.
3. Use a production WSGI server like `gunicorn`:
   ```bash
   gunicorn -w 4 -k gevent app:app
   ```
*(Note: Since WorkNet uses WebSockets, ensure your deployment platform supports WebSocket proxying and use an async worker class like `gevent` or `eventlet` with Gunicorn).*

## 🤝 Contributing

Contributions are always welcome! If you have suggestions or want to improve the codebase:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as you see fit.
