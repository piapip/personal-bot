from configs.automation_configs import (
    LOBBY_URL,
    LOGIN_SECTION_SELECTOR,
    LOGIN_BUTTON_SELECTOR,
    PLAY_BUTTON,
    WORLD_SELECTOR,
    SLEEP_TIME_AFTER_LOAD,
    RETRY_INTERVAL,
    ELEMENT_LOADING_TIMEOUT,
    USERNAME,
    PASSWORD,
)
from helpers.action import (
    sleep,
)
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

class Driver:
    def __init__(self, dry_run=bool) -> None:
        if dry_run:
            self.dry_run=True
            print("Initiate dry browser...")
            return
        print("Initiating Firefox browser. Please wait...")
        self.dry_run=False
        self.driver = webdriver.Firefox()


    # __check_dry_run is the wrapper that aborts the action
    # if the Driver is in the dry_run mode.
    def __check_dry_run(func):
        def wrapper(*args, **kwargs):
            self: Driver = args[0]
            if self.dry_run:
                print("Dry run, doing nothing...")
                return None
            else:
                return func(*args, **kwargs)
        return wrapper


    @__check_dry_run
    def goto(self, link: str):
        # goto redirect the browser to the given link.
        self.driver.get(link)
        sleep(SLEEP_TIME_AFTER_LOAD)
        

    @__check_dry_run
    def login(self):
        # Go into the page.
        self.goto(LOBBY_URL)
        elemLogin = self.getElementByValue(selector=LOGIN_SECTION_SELECTOR, value="Log in")
        sleep(0.1)
        elemLogin.click()
        sleep(0.1)
        
        # Type in email and password
        elemEmail = self.getElementByName(name="email")
        elemPassword = self.getElementByName(name="password")
        
        sleep(0.1)
        elemEmail.send_keys(USERNAME)
        sleep(0.1)
        elemPassword.send_keys(PASSWORD)
        sleep(0.2)

        self.getElementByCSS(LOGIN_BUTTON_SELECTOR).click()

        # After logging in, direct to the list of the server.
        # And click on the thing.
        self.getElementByCSS(PLAY_BUTTON).click()
        sleep(SLEEP_TIME_AFTER_LOAD)


    @__check_dry_run
    def getElementByName(self, name: str) -> WebElement:
        # Ikariam is very laggy, so if it's timeout, let's refresh once and try again.
        try:
            elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.NAME, name), message="timeout finding input for name: " + name)
        except Exception:
            self.driver.refresh()
            sleep(RETRY_INTERVAL)
            try:
                elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.NAME, name), message="timeout finding input for name: " + name)
            except Exception as e:
                raise Exception("failed to get element by name ({}): {}".format(name, e))
            
        return elem
    

    @__check_dry_run
    def clickByName(self, name: str) -> None:
        print("executing click by name")
        try:
            self.getElementByName(name).click()
        except Exception as e:
            raise Exception("failed to click element by name ({}) due to: {}".format(name, e))
        

    @__check_dry_run
    def getElementByCSS(self, selector: str) -> WebElement:
        # Ikariam is very laggy, so if it's timeout, let's refresh once and try again.
        try:
            elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.CSS_SELECTOR, selector), message="timeout finding the selector for: " + selector)
        except Exception:
            self.driver.refresh()
            sleep(RETRY_INTERVAL)
            try:
                elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.CSS_SELECTOR, selector), message="timeout finding the selector for: " + selector)
            except Exception as e:
                raise Exception("failed to get element by css ({}): {}".format(selector, e.Message))
        
        return elem


    @__check_dry_run
    def clickByCSS(self, selector: str) -> None:
        print("executing click by selector")
        try:
            self.getElementByCSS(selector=selector).click()
        except Exception as e:
            raise Exception("failed to click element by css ({}) due to: {}".format(selector, e))


    @__check_dry_run
    def getElementByValue(self, selector: str, value: str) -> WebElement:
        # Ikariam is very laggy, so if it's timeout, let's refresh once and try again. 
        try:
            elements = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_elements(by=By.CSS_SELECTOR, value=selector), message="timeout finding the selector for: " + selector)
        except Exception:
            self.driver.refresh()
            sleep(RETRY_INTERVAL)
            try:
                elements = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_elements(by=By.CSS_SELECTOR, value=selector), message="timeout finding the selector for: " + selector)
            except Exception as e:
                raise Exception("failed to get element by selector ({}) - value ({}): {}".format(selector, value, e))
        
        for e in elements:
            if e.text == value:
                return e
        
        raise Exception("selector ({}) - value ({}) not found".format(selector, value))


    @__check_dry_run
    def clickByValue(self, selector: str, value: str):
        print("executing click by value")
        try:
            self.getElementByValue(selector=selector, value=value).click()
        except Exception as e:
            raise Exception("failed to click element by value ({})-({}) due to: {}".format(selector, value, e))

    
    def countTabs(self) -> int:
        if self.dry_run:
            return 0

        return len(self.driver.window_handles)


    @__check_dry_run
    def switchTab(self, tab_index: int):
        print("switching tab")
        try:
            current_tab_counts = self.countTabs()
            if tab_index >= current_tab_counts:
                raise Exception("tab index must be less than {}".format(current_tab_counts)) 
            
            self.driver.switch_to.window(self.driver.window_handles[tab_index])
        except Exception as e:
            raise Exception("failed to switch tab to index {} due to: {}".format(tab_index, e))


    @__check_dry_run
    def close(self):
        # self.driver.close() # this only close 1 tab.
        self.driver.quit()
