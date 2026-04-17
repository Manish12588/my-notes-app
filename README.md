# NoteVault 📚

A multi-user notes app for learning — each user has their own private, isolated note space.

## Tech Stack
- **Backend**: Python 3 + Flask
- **Database**: SQLite (zero-config, file-based via SQLAlchemy)
- **ORM**: Flask-SQLAlchemy
- **Auth**: Flask-Login + Werkzeug password hashing
- **Frontend**: HTML5, Vanilla CSS (Flexbox/Grid), Google Fonts (DM Serif Display + DM Sans)

## Project Structure
```
Notes-app/
├── app.py              # Main Flask application and routing
├── models.py           # SQLAlchemy database models (User, Note)
├── requirements.txt    # Python package dependencies
├── README.md           # Project documentation
├── static/
│   └── style.css       # Custom styling and animations
└── templates/
    ├── base.html       # Base layout (navbar, footer, flash messages)
    ├── index.html      # Note dashboard and search interface
    ├── register.html   # User registration form
    ├── login.html      # User login form
    ├── add_note.html   # Note creation form
    ├── edit_note.html  # Note editing form
    └── view_note.html  # Full-screen note viewer
```

## Features
- 🔐 User registration & login (each user sees ONLY their own notes)
- ✏️ Create, view, edit, delete notes
- 📌 Pin important notes to the top
- 🏷️ Custom categories with sidebar filtering
- 🔍 Full-text search (title + content)
- 📊 Live word & character count in editor
- 📱 Responsive design (mobile-friendly)

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

The SQLite database (`notes.db`) is created automatically on first run inside an `instance/` folder.

## Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/register` | Create a new account |
| GET/POST | `/login` | Log in |
| GET | `/logout` | Log out |
| GET | `/` | Dashboard (with search & filter) |
| GET/POST | `/note/add` | Create a note |
| GET | `/note/<id>` | View a note |
| GET/POST | `/note/<id>/edit` | Edit a note |
| POST | `/note/<id>/delete` | Delete a note |
| POST | `/note/<id>/pin` | Toggle pin (JSON) |
