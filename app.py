from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

from models import db, User, Note

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY']                  = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI']     = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view      = 'login'
login_manager.login_message   = 'Please log in to access your notes.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ── Auth routes ────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm',  '')

        error = None
        if not username or len(username) < 3:
            error = 'Username must be at least 3 characters.'
        elif not email or '@' not in email:
            error = 'Enter a valid email address.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif User.query.filter_by(username=username).first():
            error = 'Username already taken.'
        elif User.query.filter_by(email=email).first():
            error = 'Email already registered.'

        if error:
            flash(error, 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Welcome, {username}! Your account has been created.', 'success')
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password',   '')
        remember   = bool(request.form.get('remember'))

        user = (User.query.filter_by(username=identifier).first() or
                User.query.filter_by(email=identifier.lower()).first())

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username/email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ── Note dashboard ─────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    search   = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    pinned_only = request.args.get('pinned', '')

    query = Note.query.filter_by(user_id=current_user.id)

    if search:
        like = f'%{search}%'
        query = query.filter((Note.title.ilike(like)) | (Note.content.ilike(like)))
    if category:
        query = query.filter_by(category=category)
    if pinned_only:
        query = query.filter_by(pinned=True)

    notes      = query.order_by(Note.pinned.desc(), Note.updated_at.desc()).all()
    categories = (db.session.query(Note.category)
                  .filter(Note.user_id == current_user.id, Note.category.isnot(None))
                  .distinct().order_by(Note.category).all())
    categories = [c[0] for c in categories]

    return render_template('index.html',
                           notes=notes,
                           categories=categories,
                           search=search,
                           active_category=category,
                           pinned_only=bool(pinned_only))


# ── Note CRUD (form-based) ─────────────────────────────────────────────────

@app.route('/note/add', methods=['GET', 'POST'])
@login_required
def add_note():
    categories = (db.session.query(Note.category)
                  .filter(Note.user_id == current_user.id, Note.category.isnot(None))
                  .distinct().order_by(Note.category).all())
    categories = [c[0] for c in categories]

    if request.method == 'POST':
        title    = request.form.get('title',    '').strip() or 'Untitled'
        content  = request.form.get('content',  '')
        category = request.form.get('category', '').strip() or None
        new_cat  = request.form.get('new_category', '').strip()
        pinned   = bool(request.form.get('pinned'))

        if new_cat:
            category = new_cat

        note = Note(title=title, content=content, category=category,
                    pinned=pinned, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('view_note', note_id=note.id))

    return render_template('add_note.html', categories=categories)


@app.route('/note/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return render_template('view_note.html', note=note)


@app.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    categories = (db.session.query(Note.category)
                  .filter(Note.user_id == current_user.id, Note.category.isnot(None))
                  .distinct().order_by(Note.category).all())
    categories = [c[0] for c in categories]

    if request.method == 'POST':
        note.title    = request.form.get('title',    '').strip() or 'Untitled'
        note.content  = request.form.get('content',  '')
        category      = request.form.get('category', '').strip() or None
        new_cat       = request.form.get('new_category', '').strip()
        note.pinned   = bool(request.form.get('pinned'))
        note.updated_at = datetime.utcnow()

        if new_cat:
            category = new_cat
        note.category = category

        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('view_note', note_id=note.id))

    return render_template('edit_note.html', note=note, categories=categories)


@app.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'info')
    return redirect(url_for('index'))


@app.route('/note/<int:note_id>/pin', methods=['POST'])
@login_required
def toggle_pin(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    note.pinned = not note.pinned
    db.session.commit()
    return jsonify({'pinned': note.pinned})


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
