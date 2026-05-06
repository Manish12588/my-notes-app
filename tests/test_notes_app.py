import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, TEST_USER, TEST_PASS, TEST_EMAIL


class TestAuth:

    def test_register_page_loads(self, driver):
        driver.get(f"{BASE_URL}/register")
        assert "Create Account" in driver.title
        assert driver.find_element(By.ID, "username").is_displayed()
        assert driver.find_element(By.ID, "email").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()

    def test_register_new_user(self, driver):
        driver.get(f"{BASE_URL}/register")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(TEST_USER)
        driver.find_element(By.ID, "email").send_keys(TEST_EMAIL)
        driver.find_element(By.ID, "password").send_keys(TEST_PASS)
        driver.find_element(By.ID, "confirm").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        # Should redirect to login after registration
        wait.until(lambda d: "login" in d.current_url or "Notes" in d.title)
        assert "login" in driver.current_url or "NoteVault" in driver.title

    def test_login_page_loads(self, driver):
        # Logout first to ensure we're not redirected
        driver.get(f"{BASE_URL}/logout")
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "identifier")))
        assert "Login" in driver.title
        assert driver.find_element(By.ID, "identifier").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()

    def test_successful_login(self, driver):
        driver.get(f"{BASE_URL}/logout")
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "identifier")))
        driver.find_element(By.ID, "identifier").send_keys(TEST_USER)
        driver.find_element(By.ID, "password").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        wait.until(EC.url_to_be(f"{BASE_URL}/"))
        assert driver.current_url == f"{BASE_URL}/"

    def test_invalid_login(self, driver):
        driver.get(f"{BASE_URL}/logout")
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "identifier")))
        driver.find_element(By.ID, "identifier").send_keys("wronguser")
        driver.find_element(By.ID, "password").send_keys("wrongpass")
        driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".flash.flash-error")))
        error = driver.find_element(By.CSS_SELECTOR, ".flash.flash-error")
        assert error.is_displayed()


class TestNotes:

    def test_dashboard_loads(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.title_contains("Notes"))
        assert "My Notes" in logged_in_driver.title
        assert logged_in_driver.find_element(
            By.CSS_SELECTOR, "a.btn-nav-new"
        ).is_displayed()

    def test_add_note_page_loads(self, logged_in_driver):
        logged_in_driver.get(f"{BASE_URL}/note/add")
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "title")))
        assert "New Note" in logged_in_driver.title
        assert logged_in_driver.find_element(By.ID, "title").is_displayed()
        assert logged_in_driver.find_element(By.ID, "content").is_displayed()

    def test_create_note(self, logged_in_driver):
        logged_in_driver.get(f"{BASE_URL}/note/add")
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "title")))
        logged_in_driver.find_element(By.ID, "title").send_keys("Test Note Title")
        logged_in_driver.find_element(By.ID, "content").send_keys("This is test note content.")
        logged_in_driver.find_element(By.CSS_SELECTOR, "button.btn-primary").click()
        # Flask redirects to view page after save
        wait.until(EC.title_contains("NoteVault"))
        assert "NoteVault" in logged_in_driver.title

    def test_search_note(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='q']")))
        search = logged_in_driver.find_element(By.CSS_SELECTOR, "input[name='q']")
        search.clear()
        search.send_keys("Test Note Title")
        search.submit()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".note-card")))
        cards = logged_in_driver.find_elements(By.CSS_SELECTOR, ".note-card")
        assert len(cards) >= 1

    def test_view_note(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-link")))
        logged_in_driver.find_element(By.CSS_SELECTOR, ".card-link").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".view-title")))
        assert logged_in_driver.find_element(By.CSS_SELECTOR, ".view-title").is_displayed()
        assert logged_in_driver.find_element(By.CSS_SELECTOR, ".view-content").is_displayed()

    def test_edit_note(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-btn")))
        logged_in_driver.find_element(By.CSS_SELECTOR, ".card-btn").click()
        wait.until(EC.visibility_of_element_located((By.ID, "title")))
        title_input = logged_in_driver.find_element(By.ID, "title")
        title_input.clear()
        title_input.send_keys("Updated Test Note Title")
        logged_in_driver.find_element(By.CSS_SELECTOR, "button.btn-primary").click()
        # Flask redirects to view page after update
        wait.until(EC.title_contains("NoteVault"))
        assert "NoteVault" in logged_in_driver.title

    def test_sidebar_all_notes_link(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.sidebar-link")))
        all_notes = logged_in_driver.find_element(By.CSS_SELECTOR, "a.sidebar-link")
        assert all_notes.is_displayed()

    def test_logout(self, logged_in_driver):
        logged_in_driver.get(BASE_URL)
        wait = WebDriverWait(logged_in_driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.btn-logout")))
        logged_in_driver.find_element(By.CSS_SELECTOR, "a.btn-logout").click()
        wait.until(EC.url_contains("login"))
        assert "login" in logged_in_driver.current_url
