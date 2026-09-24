from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Core.models import Hospital, HazardReport

import uuid


User = get_user_model()


class FHAPTSeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = Options()
        options.add_argument("--start-maximized")

        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.password = "TestPassword123!"

        unique_id = uuid.uuid4().hex[:8]

        self.username = f"selenium_user_{unique_id}"
        self.email = f"selenium_{unique_id}@example.com"

        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

    def test_01_home_page_loads(self):
        self.driver.get(self.live_server_url)

        self.assertIn("FHPTS", self.driver.title)

    def test_02_login_page_loads(self):
        self.driver.get(
            self.live_server_url + "/login/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "email")
            )
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "password")
            )
        )

        self.assertIn(
            "Sign In",
            self.driver.page_source
        )

    # =========================================================
    # TC-03: USER LOGIN
    # =========================================================

    def test_03_user_can_login(self):
        self.driver.get(
            self.live_server_url + "/login/"
        )

        email_input = self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "email")
            )
        )

        password_input = self.driver.find_element(
            By.NAME,
            "password"
        )

        email_input.send_keys(
            self.email
        )

        password_input.send_keys(
            self.password
        )

        password_input.submit()

        self.wait.until(
            lambda driver:
            driver.current_url !=
            self.live_server_url + "/login/"
        )

        self.assertNotEqual(
            self.driver.current_url,
            self.live_server_url + "/login/"
        )

    # =========================================================
    # TC-04: USER REGISTRATION
    # =========================================================

    def test_04_user_registration(self):

        self.driver.get(
            self.live_server_url + "/register/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "form")
            )
        )

        unique_id = uuid.uuid4().hex[:8]

        username = f"new_user_{unique_id}"
        email = f"new_user_{unique_id}@example.com"

        self.driver.find_element(
            By.NAME,
            "username"
        ).send_keys(
            username
        )

        self.driver.find_element(
            By.NAME,
            "email"
        ).send_keys(
            email
        )

        self.driver.find_element(
            By.NAME,
            "password1"
        ).send_keys(
            self.password
        )

        self.driver.find_element(
            By.NAME,
            "password2"
        ).send_keys(
            self.password
        )

        self.driver.find_element(
            By.NAME,
            "phone"
        ).send_keys(
            "01700000000"
        )

        self.driver.find_element(
            By.NAME,
            "address"
        ).send_keys(
            "Noakhali, Bangladesh"
        )

        self.driver.find_element(
            By.CSS_SELECTOR,
            "button[type='submit']"
        ).click()

        self.wait.until(
            lambda driver:
            driver.current_url !=
            self.live_server_url + "/register/"
        )

        self.assertNotEqual(
            self.driver.current_url,
            self.live_server_url + "/register/"
        )

    # =========================================================
    # TC-05: USER LOGOUT
    # =========================================================

    def test_05_user_logout(self):

        self.driver.get(
            self.live_server_url + "/login/"
        )

        self.driver.find_element(
            By.NAME,
            "email"
        ).send_keys(
            self.email
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).send_keys(
            self.password
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).submit()

        self.wait.until(
            lambda driver:
            driver.current_url !=
            self.live_server_url + "/login/"
        )

        # Actual project route:
        # /logout/
        self.driver.get(
            self.live_server_url + "/logout/"
        )

        self.wait.until(
            lambda driver:
            "/login/" in driver.current_url
            or "login" in driver.page_source.lower()
        )

        self.assertTrue(
            "/login/" in self.driver.current_url
            or "login" in self.driver.page_source.lower()
        )

    # =========================================================
    # TC-06: LOGIN FORM VALIDATION
    # =========================================================

    def test_06_login_requires_credentials(self):

        self.driver.get(
            self.live_server_url + "/login/"
        )

        email_input = self.driver.find_element(
            By.NAME,
            "email"
        )

        password_input = self.driver.find_element(
            By.NAME,
            "password"
        )

        self.assertIsNotNone(
            email_input.get_attribute("required")
        )

        self.assertIsNotNone(
            password_input.get_attribute("required")
        )

    # =========================================================
    # TC-07: REGISTER PAGE
    # =========================================================

    def test_07_register_page_loads(self):

        self.driver.get(
            self.live_server_url + "/register/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "username")
            )
        )

        self.assertIn(
            "Create your account",
            self.driver.page_source
        )

    # =========================================================
    # TC-08: UNAUTHENTICATED ACCESS CONTROL
    # =========================================================

    def test_08_unauthenticated_user_access_control(self):
    
        self.driver.get(
            self.live_server_url + "/admin_dashboard/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        page_source = self.driver.page_source.lower()
        current_url = self.driver.current_url.lower()

        # Unauthenticated users should not receive
        # the actual admin dashboard content.
        dashboard_indicators = [
            "admin dashboard",
            "manage user roles",
            "user management",
            "hospital management",
        ]

        has_dashboard_content = any(
            indicator in page_source
            for indicator in dashboard_indicators
        )

        # Either redirected to login or dashboard content
        # is not exposed to an unauthenticated user.
        access_protected = (
            "/login/" in current_url
            or not has_dashboard_content
        )

        self.assertTrue(access_protected)
    # =========================================================
    # TC-09: ADMIN LOGIN
    # =========================================================

    def test_09_admin_login(self):

        unique_id = uuid.uuid4().hex[:8]

        admin_email = (
            f"selenium_admin_{unique_id}@example.com"
        )

        admin_username = (
            f"selenium_admin_{unique_id}"
        )

        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=self.password
        )

        self.driver.get(
            self.live_server_url + "/login/"
        )

        self.driver.find_element(
            By.NAME,
            "email"
        ).send_keys(
            admin_email
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).send_keys(
            self.password
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).submit()

        self.wait.until(
            lambda driver:
            driver.current_url !=
            self.live_server_url + "/login/"
        )

        self.assertNotEqual(
            self.driver.current_url,
            self.live_server_url + "/login/"
        )

    # =========================================================
    # TC-10: DJANGO ADMIN LOGIN PAGE
    # =========================================================

    def test_10_admin_site_loads(self):

        self.driver.get(
            self.live_server_url + "/admin/login/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "username")
            )
        )

        self.assertIn(
            "Django",
            self.driver.page_source
        )

    # =========================================================
    # TC-11: ACTIVE HAZARD PAGE
    # =========================================================

    def test_11_active_hazard_page(self):

        self.driver.get(
            self.live_server_url + "/active_hazard/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        self.assertNotIn(
            "404 | FHAPTS",
            self.driver.title
        )

    # =========================================================
    # TC-12: MISSING COMPLAINT PAGE
    # =========================================================

    def test_12_missing_complaint_page(self):

        hazard = HazardReport.objects.create(
            title="Selenium Test Hazard",
            description="Automated testing hazard",
            user=self.user,
            servity="Low",
            status="active",
        )

        self.driver.get(
            self.live_server_url +
            f"/missing_complaint/{hazard.id}/missing/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        self.assertNotIn(
            "404 | FHAPTS",
            self.driver.title
        )

    # =========================================================
    # TC-13: EMERGENCY REPORT PAGE
    # =========================================================

    def test_13_emergency_report_page(self):

        self.driver.get(
            self.live_server_url +
            "/emergency-report/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        self.assertNotIn(
            "404 | FHAPTS",
            self.driver.title
        )

    # =========================================================
    # TC-14: HOSPITAL DETAILS PAGE
    # =========================================================

    def test_14_hospital_page(self):

        self.driver.get(
            self.live_server_url +
            "/hospital_details/"
        )

        self.wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        self.assertNotIn(
            "404 | FHAPTS",
            self.driver.title
        )

    # =========================================================
    # TC-15: INVALID LOGIN
    # =========================================================

    def test_15_invalid_login(self):

        self.driver.get(
            self.live_server_url + "/login/"
        )

        self.driver.find_element(
            By.NAME,
            "email"
        ).send_keys(
            "wrong@example.com"
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).send_keys(
            "WrongPassword123!"
        )

        self.driver.find_element(
            By.NAME,
            "password"
        ).submit()

        # User should remain on login page
        self.wait.until(
            EC.presence_of_element_located(
                (By.NAME, "email")
            )
        )

        self.assertIn(
            "/login/",
            self.driver.current_url
        )