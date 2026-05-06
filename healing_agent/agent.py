"""
agent.py — Self-Healing Test Agent (Step-by-step mode)
LLM is used ONLY for reasoning about the correct locator.
All tool calls are explicit — no autonomous decision making needed.
"""

import warnings
warnings.filterwarnings("ignore")
import subprocess
import re
import json
import sys
import os

from langchain_ollama import ChatOllama
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL       = "http://localhost:5000"
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "../tests/test_notes_app.py")
TEST_DIR       = os.path.join(os.path.dirname(__file__), "../tests")

# URL mapping for pages
PAGE_URLS = {
    "login":    f"{BASE_URL}/login",
    "register": f"{BASE_URL}/register",
    "dashboard": BASE_URL,
    "add_note": f"{BASE_URL}/note/add",
}


def run_tests():
    print("🔍 Running test suite...\n")
    result = subprocess.run(
        ["pytest", "test_notes_app.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=TEST_DIR
    )
    return result.stdout + result.stderr


def parse_failures(output):
    """Extract broken locators and their page from pytest output."""
    failures = []
    lines = output.split("\n")
    for line in lines:
        # Look for lines like: test_notes_app.py:35: in test_login_page_loads
        if 'By.ID, "' in line or "By.CSS_SELECTOR" in line:
            match = re.search(r'(By\.\w+,\s*["\'][^"\']+["\'])', line)
            if match:
                locator = match.group(1)
                # Determine which page based on test name context
                page = "login"  # default
                if "register" in line:
                    page = "register"
                elif "dashboard" in line or "note" in line:
                    page = "dashboard"
                failures.append({"locator": locator, "page": page})
    return failures


def capture_dom(url):
    """Capture and return simplified DOM from a URL."""
    print(f"🌐 Capturing DOM from {url}...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    try:
        driver.get(url)
        import time; time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        elements = []
        for tag in soup.find_all(["input", "button", "select", "textarea"]):
            attrs = {k: v for k, v in tag.attrs.items()
                     if k in ["id", "name", "type", "class"]}
            if attrs:
                elements.append({"tag": tag.name, "attrs": attrs})
        return json.dumps(elements, indent=2)
    finally:
        driver.quit()


def ask_llm_for_fix(broken_locator, dom_elements, page):
    """Ask LLM: given this DOM, what is the correct replacement for this locator?"""
    print(f"🤖 Asking LLM to find correct locator for: {broken_locator}\n")
    llm = ChatOllama(model="qwen2.5:3b", temperature=0, num_ctx=2048)

    prompt = f"""You are a test automation expert.

        A Selenium test is failing because this locator does not exist on the page:
        BROKEN: {broken_locator}

        Here are the actual elements found on the {page} page:
        {dom_elements}

        What is the correct replacement locator?
        Reply with ONLY the replacement string in this exact format:
        By.ID, "correct-id"
        or
        By.CSS_SELECTOR, "correct-selector"

        Nothing else. No explanation.
        """

    response = llm.invoke(prompt)
    return response.content.strip()


def patch_file(old_locator, new_locator):
    """Replace broken locator in test file."""
    with open(TEST_FILE_PATH, "r") as f:
        content = f.read()

    if old_locator not in content:
        print(f"⚠️  Locator not found: {old_locator}")
        return 0

    count = content.count(old_locator)
    new_content = content.replace(old_locator, new_locator)

    with open(TEST_FILE_PATH, "w") as f:
        f.write(new_content)

    print(f"✅ Patched {count} occurrence(s): '{old_locator}' → '{new_locator}'\n")
    return count


def main():
    print("\n🔧 Self-Healing Test Agent")
    print("=" * 50)

    # Step 1 — Run tests
    output = run_tests()
    print(output)

    # Step 2 — Check if all passed
    if "failed" not in output:
        print("✅ All tests passed. Nothing to heal.")
        return

    # Step 3 — Find broken locators from test output
    # Parse directly from test file for broken By.ID references
    with open(TEST_FILE_PATH, "r") as f:
        test_content = f.read()

    # Find all unique broken locators by checking which ones cause failures
    broken = re.findall(r'By\.ID,\s*"([^"]+)"', output)
    broken = list(set(broken))

    if not broken:
        print("⚠️  Could not identify broken locators automatically.")
        return

    print(f"🔎 Broken locators found: {broken}\n")

    # Step 4 — For each broken locator, capture DOM and ask LLM
    for locator_value in broken:
        broken_locator = f'By.ID, "{locator_value}"'

        # Determine page URL
        url = PAGE_URLS["login"]  # login page for identifier issues

        # Step 5 — Capture DOM
        dom = capture_dom(url)

        # Step 6 — Ask LLM for correct locator
        new_locator = ask_llm_for_fix(broken_locator, dom, "login")
        print(f"💡 LLM suggests: {new_locator}\n")

        # Step 7 — Patch the file
        patched = patch_file(broken_locator, new_locator)

        if patched == 0:
            print("⚠️  No changes made. Skipping rerun.")
            continue

        # Step 8 — Rerun tests
        print("🔄 Rerunning tests after patch...\n")
        rerun_output = run_tests()
        print(rerun_output)

        if "failed" not in rerun_output:
            print("🎉 All tests passing! Self-healing complete.")
            return
        else:
            print("⚠️  Tests still failing after patch. Rolling back...")
            patch_file(new_locator, broken_locator)

    print("❌ Could not fully heal the test suite automatically.")


if __name__ == "__main__":
    main()
