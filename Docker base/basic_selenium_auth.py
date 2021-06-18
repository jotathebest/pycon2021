from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display

import time


class BaseBrowserCheck(object):
    def __init__(self):
        self.browser = None

    def _init_browser(self):
        """
        Initializes the browser instance
        """

        chrome_options = webdriver.ChromeOptions()
        display = Display(visible=0, size=(1386, 768))
        display.start()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_options.add_experimental_option("prefs", {"download.prompt_for_download": False})

        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_window_size(1386, 768)

    def setup_selenium(self):
        self._init_browser()

    def stop_selenium(self):
        self.browser.quit()

class WebElementCheck(BaseBrowserCheck):
    def __init__(self):
        super(WebElementCheck, self).__init__()

    def _search_element(self, selector_type, descriptor, timeout=60):
        """
        @selector_type is any of the available selectors set at selenium.webdriver.common.by utility
        @descriptor is the web element descriptor that fits the selector type, for example, if you
        search by CSS the descriptor should be a CSS selector
        """
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((selector_type, descriptor)))

            root_elements = self.browser.find_elements(selector_type, descriptor)

            # Checks if the root div was loaded
            return len(root_elements) > 0

        except (TimeoutException):
            return False

    def _does_webelement_with_xpath_exist(self, xpath, timeout=60):
        """
        Checks if a web element is loaded. Element must be referenced by its xpath
        Returns True if the element is found
        @xpath is the web element absolute path
        @timeout is the number of seconds to wait befor of throwing an exception
        """
        return self._search_element(By.XPATH, xpath, timeout=timeout)

    def _does_webelement_with_css_exist(self, css_selector, timeout=60):
        """
        Checks if a web element is loaded. Element must be referenced by its xpath
        Returns True if the element is found
        @css_selector is the CSS selector of the element
        @timeout is the number of seconds to wait befor of throwing an exception
        """
        return self._search_element(By.CSS_SELECTOR, css_selector, timeout=timeout)

    def _does_element_with_name_exists(self, web_element_name):
        try:
            self.browser.find_element_by_name(web_element_name)
            return True
        except (NoSuchElementException):
            return False

class UbiSignInCheck(WebElementCheck):
    def __init__(
        self,
        username,
        password,
        sign_url="https://industrial.ubidots.com",
        timeout=25,
    ):
        """
        @components: Status page components to update, should be an ids list, [id, id, id]
        """
        super(WebElementCheck, self).__init__()
        self.sign_url = sign_url
        self.username = username
        self.password = password
        self.timeout = timeout

    def _sign_in(self):
        """
        @timeout is the number of seconds to wait befor of throwing an exception
        """

        # Verifies if it is already signed
        current_url = self.browser.current_url
        if "app" in current_url or "dashboard" in current_url.lower():
            print("The user is already logged")
            return True

        print("Loading SigIn form")
        self.browser.get(self.sign_url)

        # Waits until form div is loaded
        is_sign_in_form_loaded = self._does_webelement_with_css_exist("form", timeout=self.timeout)
        if not is_sign_in_form_loaded:
            print(f"Could not load the form to make sign in at {self.sign_url}")
            return False

        time.sleep(1)  # Gives an additional seconds
        print("Filling form")
        if not self._does_element_with_name_exists("identification") or not self._does_element_with_name_exists(
            "password"
        ):
            print("Could not find form expected fields to make login")
            return False

        user_box = self.browser.find_element_by_name("identification")
        pass_box = self.browser.find_element_by_name("password")

        user_box.send_keys(self.username)
        pass_box.send_keys(self.password)

        if not self._does_webelement_with_xpath_exist('//button[text()="Sign In"]', timeout=self.timeout):
            print("Could not find button to make login")
            return False

        self.browser.find_element_by_xpath('//button[text()="Sign In"]').click()

        # Should redirect to the dashboards tab
        result = "dashboards" in self.browser.title.lower()
        if not result:
            print('Could not find "dashboards" label in browser tab')
        return result


    def _check(self):
        """
        Returns True if sign in feature is Ok
        """
        if self.browser is None:
            self._init_browser()

        print("Checking if the browser can make login")

        # Test 1: Should sign in using the form, signed should be True
        signed = self._sign_in()
        print("Finished, [signed = {}]".format(signed))

        return signed

    def test(self):
        login_service_up = self._check()
        attempts = 0

        while attempts < 2 and not login_service_up:  # Attempts three times to make login
            print("Checking web access, attempt: {}".format(attempts))
            login_service_up = self._check()
            attempts += 1

        check_result = {
            "result": "ok",
            "details": "",
            "create_incident": False,
        }

        if not login_service_up:  # Could not login or load root div
            details = "[Alert] Could not make login"
            print(details)
            check_result["result"] = "outage"
            check_result["create_incident"] = True
            print("Finished")
            return check_result

        print("Finished")

        return check_result

    def close_browser(self):
        self.browser.close()

if __name__ == "__main__":
    tester = UbiSignInCheck("", "")
    print(tester.test())
    time.sleep(10)
    tester.close_browser()
