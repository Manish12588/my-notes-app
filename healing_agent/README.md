# 🔧 Self-Healing Test Agent

An AI agent that **automatically detects and fixes broken Selenium locators** without any human intervention.

When a UI element's `id` or `class` changes between deployments, tests break. Instead of manually hunting down the broken locator, this agent:

1. Runs the test suite and detects failures
2. Captures the current DOM of the failing page
3. Asks an LLM to identify the correct locator from the actual page elements
4. Patches the test file automatically
5. Reruns the tests to verify the fix

---

## 💡 How it works

```
pytest fails (locator not found)
    └─► Agent captures /login DOM via headless Chrome
            └─► LLM answers: "given this DOM, what replaces the broken locator?"
                    └─► Agent patches test_notes_app.py
                            └─► pytest reruns → 13/13 passing
```

**Key design principle:** The LLM does ONE thing — identify the correct locator from the DOM. Everything else (running tests, capturing DOM, patching files, rerunning) is plain Python. This makes the agent fast, reliable, and easy to debug.

---

## 📁 Folder structure

```
healing_agent/
├── agent.py          # Main self-healing agent
├── tools.py          # DOM capture and file patch utilities
├── requirements.txt  # Agent dependencies
└── README.md         # This file
```

---

## ⚙️ Prerequisites

- Python 3.10+
- Google Chrome installed
- Ollama installed and running — [download here](https://ollama.com/download)
- NoteVault app running at `http://localhost:5000`
- Selenium test suite set up in `tests/`

Pull the required model:

```bash
ollama pull qwen2.5:3b
```

Verify Ollama is running:

```bash
ollama list
```

---

## 🚀 Setup

```bash
# Install dependencies
pip install -r healing_agent/requirements.txt
```

---

## 🧪 How to demo the self-healing agent

### Step 1 — Confirm tests are passing

```bash
pytest tests/test_notes_app.py -v
```

Expected: `13 passed`

---

### Step 2 — Break a locator (simulate a UI change)

```bash
sed -i 's/By.ID, "identifier"/By.ID, "user-input"/g' tests/test_notes_app.py
```

This simulates what happens when a developer renames an HTML element — for example changing `id="identifier"` to `id="user-input"` in the login form.

Verify the tests are now broken:

```bash
pytest tests/test_notes_app.py -v 2>&1 | tail -5
```

Expected output:
```
FAILED tests/test_notes_app.py::TestAuth::test_login_page_loads
FAILED tests/test_notes_app.py::TestAuth::test_successful_login
FAILED tests/test_notes_app.py::TestAuth::test_invalid_login
3 failed, 10 passed
```

---

### Step 3 — Run the self-healing agent

```bash
python healing_agent/agent.py
```

Watch the agent work through each step:

```
🔧 Self-Healing Test Agent
==================================================
🔍 Running test suite...

3 failed, 10 passed

🔎 Broken locators found: ['user-input']

🌐 Capturing DOM from http://localhost:5000/login...
🤖 Asking LLM to find correct locator for: By.ID, "user-input"

💡 LLM suggests: By.ID, "identifier"

✅ Patched 6 occurrence(s): 'By.ID, "user-input"' → 'By.ID, "identifier"'

🔄 Rerunning tests after patch...

13 passed in 3.65s

🎉 All tests passing! Self-healing complete.
```

---

## 🧠 Agent architecture

```
main()
  │
  ├── run_tests()              # subprocess: pytest
  │       └── returns pytest output as string
  │
  ├── parse_failures()         # regex: extract broken locator values
  │       └── returns ['user-input']
  │
  ├── capture_dom(url)         # Selenium + BeautifulSoup
  │       └── returns clean JSON of page elements
  │
  ├── ask_llm_for_fix()        # Ollama (qwen2.5:3b) — ONLY AI STEP
  │       └── returns 'By.ID, "identifier"'
  │
  ├── patch_file()             # str.replace() on test file
  │       └── patches 6 occurrences
  │
  └── run_tests()              # verify fix
          └── 13 passed ✅
```

**The LLM is used for exactly one task:** given the broken locator and the actual DOM elements, what is the correct replacement? Everything else is deterministic Python.

---

## 📦 Dependencies

```
langchain-ollama      # ChatOllama — runs Ollama models in LangChain
langchain-core        # LLM invocation
selenium              # Headless browser for DOM capture
webdriver-manager     # Auto-downloads matching ChromeDriver
beautifulsoup4        # HTML parsing — extracts clean element list from DOM
```

---