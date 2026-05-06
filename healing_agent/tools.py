"""
tools.py — Docker tools for the self-healing agent.
Each function is decorated with @tool so the LLM can call them.
"""

import subprocess
import json
import re
import os
from langchain_core.tools import tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ── Constants ────────────────────────────────────────────────────────────────
BASE_URL       = "http://localhost:5000"
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "../tests/test_notes_app.py")
TEST_DIR       = os.path.join(os.path.dirname(__file__), "../tests")


# ── Helper: headless Chrome ──────────────────────────────────────────────────
def _get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ── Tool 1 ───────────────────────────────────────────────────────────────────
@tool
def run_tests() -> str:
    """
    Run the Selenium test suite and return the output.
    Returns pass/fail summary and any error messages.
    """
    result = subprocess.run(
        ["pytest", "test_notes_app.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=TEST_DIR
    )
    output = result.stdout + result.stderr
    return output


# ── Tool 2 ───────────────────────────────────────────────────────────────────
@tool
def get_failing_tests(pytest_output: str) -> str:
    """
    Parse pytest output and extract the names of failing tests
    along with their error messages.
    Input: raw pytest output string.
    Returns: JSON list of {test_name, error} dicts.
    """
    failures = []
    lines = pytest_output.split("\n")

    current_test = None
    current_error = []

    for line in lines:
        # Detect FAILED line
        if "FAILED" in line and "::" in line:
            parts = line.strip().split(" ")[0]
            current_test = parts.split("::")[-1]
            current_error = []

        # Detect NoSuchElementException
        if current_test and "NoSuchElementException" in line:
            current_error.append(line.strip())

        # Detect selector info
        if current_test and ("selector" in line.lower() or "id=" in line.lower()):
            current_error.append(line.strip())

        # End of failure block
        if current_test and line.startswith("_____"):
            if current_error:
                failures.append({
                    "test_name": current_test,
                    "error": " | ".join(current_error)
                })
            current_test = None
            current_error = []

    return json.dumps(failures, indent=2)


# ── Tool 3 ───────────────────────────────────────────────────────────────────
@tool
def capture_page_dom(url: str) -> str:
    """
    Navigate to a URL and return only form inputs and their attributes.
    Used to inspect current locators when a test fails.
    Input: full URL to capture (e.g. http://localhost:5000/login)
    """
    from bs4 import BeautifulSoup
    import time

    driver = _get_driver()
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract only interactive elements
        elements = []
        for tag in soup.find_all(["input", "button", "select", "textarea", "a", "form"]):
            attrs = {k: v for k, v in tag.attrs.items()
                     if k in ["id", "name", "type", "class", "href", "action"]}
            if attrs:
                elements.append({"tag": tag.name, "attrs": attrs})

        return json.dumps(elements, indent=2)
    finally:
        driver.quit()


# ── Tool 4 ───────────────────────────────────────────────────────────────────
@tool
def read_test_file() -> str:
    """
    Read and return the full contents of test_notes_app.py.
    Used to understand current locators before patching.
    """
    with open(TEST_FILE_PATH, "r") as f:
        return f.read()


# ── Tool 5 ───────────────────────────────────────────────────────────────────
@tool
def patch_test_file(old_locator: str, new_locator: str) -> str:
    """
    Replace a broken locator in test_notes_app.py with a new one.
    Input:
      old_locator: the exact string to find (e.g. 'By.ID, "identifier"')
      new_locator: the replacement string (e.g. 'By.ID, "user-identifier"')
    Returns: confirmation message or error.
    """
    with open(TEST_FILE_PATH, "r") as f:
        content = f.read()

    if old_locator not in content:
        return f"❌ Locator not found in test file: {old_locator}"

    count = content.count(old_locator)
    new_content = content.replace(old_locator, new_locator)

    with open(TEST_FILE_PATH, "w") as f:
        f.write(new_content)

    return f"✅ Patched {count} occurrence(s): '{old_locator}' → '{new_locator}'"


# ── Tool 6 ───────────────────────────────────────────────────────────────────
@tool
def restore_test_file(original_locator: str, bad_locator: str) -> str:
    """
    Restore a locator in test_notes_app.py to its original value.
    Used to roll back a bad patch if the rerun still fails.
    Input:
      original_locator: the correct locator to restore
      bad_locator: the incorrect locator currently in the file
    """
    with open(TEST_FILE_PATH, "r") as f:
        content = f.read()

    new_content = content.replace(bad_locator, original_locator)

    with open(TEST_FILE_PATH, "w") as f:
        f.write(new_content)

    return f"✅ Restored: '{bad_locator}' → '{original_locator}'"
