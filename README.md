# WorkNet 🚀

<div align="center">
  <img src="frontend/static/favicon.svg" width="80" height="80" alt="Ethara Logo">
  <h3>A Premium, Real-Time Team Workspace for Modern Productivity.</h3>
  <p>Built with Python, Flask, and High-Performance Async Drivers.</p>
</div>

---

## ✨ Overview

**Ethara (WorkNet)** is a polished, enterprise-grade workspace designed to help teams organize projects, assign work, and track progress effortlessly. Unlike generic task managers, Ethara focuses on **Visual Excellence** and **Real-Time Responsiveness**, providing a stunning interface that feels alive.

## 🌟 Key Features

- **Real-Time Collaboration**: Instant task updates and activity feeds powered by WebSockets (SocketIO).
- **Advanced Task Management**: Interactive Kanban boards with drag-and-drop support (SortableJS).
- **Intelligent Dashboard**: Data-driven insights with Chart.js showing project health and team productivity.
- **Dynamic Theming System**:
  - ☀️ **Light**: Clean, professional typography for focus.
  - 🌙 **Dark**: Sleek, high-tech interface for reduced eye strain.
  - 🌊 **Ocean**: Fluid glassmorphism for a modern aesthetic.
  - 🌅 **Sunset**: Bold, neo-brutalist design for creative teams.
- **Enterprise Ready**: Role-based access control, secure authentication, and full audit logs.

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Flask, SQLAlchemy
- **Database**: Supports PostgreSQL, MySQL, and SQLite (Automatic detection)
- **Real-Time**: Flask-SocketIO with Gevent drivers
- **Frontend**: Vanilla JavaScript, CSS3 (Modern Variables), HTML5
- **Deployment**: Optimized for Railway, Heroku, and Docker

## 🚀 Deployment on Railway

Ethara is pre-configured for seamless deployment on **Railway**. Follow these steps for a perfect 1-click deployment:

### 1. Environment Variables
Ensure you have the following variables set in your Railway dashboard:
- `FLASK_DEBUG`: `0`
- `DATABASE_URL`: (Automatically provided by Railway MySQL/Postgres)
- `SECRET_KEY`: (A random string to secure sessions)

### 2. Startup Command (Procfile)
Ethara uses the **App Factory Pattern** for maximum stability. The repository includes a `Procfile` that Railway uses automatically. Ensure your "Custom Start Command" in Railway is **empty** to use the default:
```bash
web: gunicorn -w 1 --worker-class gevent --timeout 120 -b 0.0.0.0:$PORT "backend.app:create_app()"
```

### 3. Compatibility Note
This project is optimized for **Python 3.13**. It uses the `gevent` engine and `gunicorn 23.0.0` to ensure stability and prevent common "Bad Gateway" errors on high-performance cloud environments.

## 💻 Local Development

### Prerequisites
- Python 3.10+
- `pip` package manager

### Setup Instructions
1. **Clone & Navigate:**
   ```bash
   git clone https://github.com/saksham998-png/Worknet.git
   cd Worknet
   ```
2. **Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Server:**
   ```bash
   python app.py
   ```
5. **Access:** Open `http://127.0.0.1:5000`

## 📂 Project Structure

- `backend/`: Core logic, routes, and models.
- `frontend/`: UI layer (static assets and Jinja2 templates).
- `app.py`: Entry point for local development.
- `Procfile`: Production configuration for cloud hosting.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for any bugs or feature requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
