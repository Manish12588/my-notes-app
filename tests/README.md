# 🧪 NoteVault — Selenium Test Suite

Automated end-to-end tests for the [NoteVault](https://github.com/Manish12588/my-notes-app) Flask application. Built with **Pytest + Selenium** — tests run headlessly against a live local instance of the app.

---

## 📁 Folder structure

```
tests/
├── conftest.py           # Pytest fixtures (driver setup, session login)
├── test_notes_app.py     # All test cases (auth + notes CRUD)
├── setup_test_user.py    # One-time script to register a test user
└── requirements.txt      # Test dependencies
```

---

## ⚙️ Prerequisites

- Python 3.10+
- Google Chrome installed
- NoteVault app running locally at `http://localhost:5000`

Start the app before running tests:

```bash
# From project root
python app/app.py

# Or via Docker Compose
docker-compose up -d
```

---

## 🚀 Setup

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Register the test user (run once before first test run)
python tests/setup_test_user.py
```

---

## ▶️ Running the tests

```bash
# Run all tests
pytest tests/test_notes_app.py -v

# Run a specific test class
pytest tests/test_notes_app.py::TestAuth -v
pytest tests/test_notes_app.py::TestNotes -v

# Run a single test
pytest tests/test_notes_app.py::TestAuth::test_successful_login -v
```

Expected output:

```
13 passed in 3.22s
```

---

## 🗂️ Test coverage

### `TestAuth` — Authentication flows

| Test | What it validates |
|---|---|
| `test_register_page_loads` | Register page renders with all fields |
| `test_register_new_user` | New user can register successfully |
| `test_login_page_loads` | Login page renders correctly |
| `test_successful_login` | Valid credentials redirect to dashboard |
| `test_invalid_login` | Wrong credentials show error message |

### `TestNotes` — Notes CRUD

| Test | What it validates |
|---|---|
| `test_dashboard_loads` | Dashboard loads with New Note button visible |
| `test_add_note_page_loads` | Add note page renders with title and content fields |
| `test_create_note` | Note can be created and saved |
| `test_search_note` | Search returns matching notes |
| `test_view_note` | Note detail page loads correctly |
| `test_edit_note` | Note title can be updated |
| `test_sidebar_all_notes_link` | Sidebar navigation link is visible |
| `test_logout` | Logout redirects to login page |

---

## 🔧 Configuration

Test credentials and base URL are defined in `conftest.py`:

```python
BASE_URL  = "http://localhost:5000"
TEST_USER = "testuser"
TEST_PASS = "testpass123"
TEST_EMAIL = "testuser@test.com"
```

To test against a deployed instance (e.g. EC2), change `BASE_URL`:

```python
BASE_URL = "http://<your-ec2-ip>:5000"
```

---

## 🧠 Design decisions

**Why `scope="session"` for the driver fixture?**
One browser instance is shared across all tests — faster execution, no repeated browser startup overhead.

**Why explicit `WebDriverWait` instead of `implicitly_wait`?**
`implicitly_wait` is unreliable in headless mode for dynamic page loads. Explicit waits target specific elements and conditions, making tests more stable.

**Why logout before auth tests?**
Flask redirects authenticated users away from `/login`. Each auth test explicitly logs out first to ensure a clean state.

---

## 📦 Dependencies

```
selenium          # Browser automation
pytest            # Test runner
webdriver-manager # Auto-downloads matching ChromeDriver
requests          # Used by setup_test_user.py
```

---
