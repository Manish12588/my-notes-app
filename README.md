# NoteVault 📚
 
A multi-user learning notes app — each user has their own private, isolated note space.
 
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)
 
---

## Tech Stack
- **Backend**: Python 3 + Flask
- **Database**: SQLite (zero-config, file-based via SQLAlchemy)
- **ORM**: Flask-SQLAlchemy
- **Auth**: Flask-Login + Werkzeug password hashing
- **Frontend**: HTML5, Vanilla CSS (Flexbox/Grid), Google Fonts (DM Serif Display + DM Sans)

## Project Structure
```
Notes-app/
├── docker-compose.yml            # Docker Compose configuration
├── .dockerignore                 # Files excluded from Docker build
├── .gitignore                    # Files excluded from Git
├── app.py                        # Main Flask application and routing
├── models.py                     # SQLAlchemy database models (User, Note)
├── requirements.txt              # Python package dependencies
├── README.md                     # Project documentation
├── docker/
│   ├── Dockerfile                # Single stage Docker build
│   └── Dockerfile.multistage     # Optimized multistage Docker build
├── static/
│   └── style.css                 # Custom styling and animations
└── templates/
    ├── base.html                 # Base layout (navbar, footer, flash messages)
    ├── index.html                # Note dashboard and search interface
    ├── register.html             # User registration form
    ├── login.html                # User login form
    ├── add_note.html             # Note creation form
    ├── edit_note.html            # Note editing form
    └── view_note.html            # Full-screen note viewer
```

## Features
- 🔐 User registration & login — each user sees **only their own notes**
- ✏️ Create, view, edit and delete notes
- 📌 Pin important notes to the top
- 🏷️ Custom categories with sidebar filtering
- 🔍 Full-text search across title and content
- 📊 Live word & character count in editor
- 📱 Responsive design — mobile friendly
- 🐳 Dockerized with optimized multistage build

## Setup

## Running Locally (Without Docker)
 
```bash
# 1. (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 1. Install dependencies
pip install -r requirements.txt
 
# 2. Run the app
python app.py
 
# 3. Open in browser
http://127.0.0.1:5000
```
The SQLite database (`notes.db`) is created automatically on first run inside an `instance/` folder.

## Running With Docker
 
### Option 1 — Docker Compose (Recommended)
 
```bash
# Build and start
docker compose up -d --build
 
# View logs
docker compose logs -f
 
# Stop
docker compose down
```

### Option 2 — Docker Run
 
```bash
# Build the image
docker build -f docker/Dockerfile.multistage -t my-notes-app .
 
# Run the container (PowerShell)
docker run -d -p 5000:5000 -v ${PWD}/instance:/app/instance --name my-notes my-notes-app:latest
 
# Run the container (CMD)
docker run -d -p 5000:5000 -v %cd%/instance:/app/instance --name my-notes my-notes-app:latest
```

**Then open:** http://localhost:5000

## Routes
| Method   | Route               | Description                      |
| -------- | ------------------- | -------------------------------- |
| GET/POST | `/register`         | Create a new account             |
| GET/POST | `/login`            | Log in                           |
| GET      | `/logout`           | Log out                          |
| GET      | `/`                 | Dashboard (with search & filter) |
| GET/POST | `/note/add`         | Create a note                    |
| GET      | `/note/<id>`        | View a note                      |
| GET/POST | `/note/<id>/edit`   | Edit a note                      |
| POST     | `/note/<id>/delete` | Delete a note                    |
| POST     | `/note/<id>/pin`    | Toggle pin (JSON)                |
