from configs.automation_configs import (
    SLEEP_TIME_AFTER_LOAD,
    ELEMENT_LOADING_TIMEOUT,

    HIGHLIGHT_ELEMENT_BORDER,
    HIGHLIGHT_ELEMENT_COLOR,
    HIGHLIGHT_ELEMENT_DURATION,
)
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from typing import List
import time

class Driver:
    def __init__(self, dry_run: bool, high_light_mode: bool) -> None:
        self.high_light_mode=high_light_mode

        if dry_run:
            self.dry_run=True
            self.high_light_mode=False
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
        time.sleep(SLEEP_TIME_AFTER_LOAD)


    @__check_dry_run
    def getElementByName(self, name: str) -> WebElement:
        # Ikariam is very laggy, so if it's timeout, let's refresh once and try again.
        try:
            elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.NAME, name), message="timeout finding input for name: " + name)
            self.highLightElements(elements=[elem])
        except TimeoutException as timeoutEx:
            raise TimeoutException("not found element by name ({}): {}".format(name, timeoutEx.msg))
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
            elem = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_element(By.CSS_SELECTOR, selector), message="timeout finding the selector for: {}".format(selector))
            self.highLightElements(elements=[elem])
        except TimeoutException as timeoutEx:
            raise TimeoutException("not found element by css ({}): {}".format(selector, timeoutEx.msg))
        except Exception as e:
            raise Exception("failed to get element by css ({}): {}".format(selector, e))
            
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
        try:
            elements = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_elements(by=By.CSS_SELECTOR, value=selector), message="timeout finding the selector for: {}".format(selector))
            self.highLightElements(elements=elements)
        except TimeoutException as timeoutEx:
            raise TimeoutException("not found elements list by selector ({}): {}".format(selector, timeoutEx.msg))
        except Exception as e:
            raise Exception("failed to list element by selector ({}): {}".format(selector, e))
        
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
    def getByAttribute(self, selector: str, html_attribute: str, value: str) -> WebElement:
        try:
            elements = WebDriverWait(driver=self.driver, timeout=ELEMENT_LOADING_TIMEOUT).until(lambda x: x.find_elements(by=By.CSS_SELECTOR, value=selector), message="timeout finding the selector for: {}".format(selector))
            self.highLightElements(elements=elements)
        except TimeoutException as timeoutEx:
            raise TimeoutException("not found elements list by selector ({}): {}".format(selector, timeoutEx.msg))
        except Exception as e:
            raise Exception("failed to list element by selector ({}): {}".format(selector, e))
        
        print("strict lookup...")
        for e in elements:
            # print("html_attribute: {}".format(e.get_attribute(html_attribute)))
            if e.get_attribute(html_attribute) == value:
                print("got strict html_attribute: {}".format(e.text))
                return e

        print("partial lookup...")
        for e in elements:
            # print("html_attribute: {}".format(e.get_attribute(html_attribute)))
            if value in e.get_attribute(html_attribute):
                print("got partial html_attribute: {}".format(e.text))
                return e

        raise Exception("selector ({}) - attribute ({}) - value ({}) not found".format(selector, html_attribute, value))
    

    @__check_dry_run
    def clickByAttribute(self, selector: str, html_attribute: str, value: str) -> None:
        print("executing click by attribute")
        try:
            self.getByAttribute(selector=selector, value=value, html_attribute=html_attribute).click()
        
        except Exception as e:
            raise Exception("failed to click element by attribute ({}) due to: {}".format(selector, e))


    @__check_dry_run
    def textInput(self, selector: str, value: str) -> None:
        print("typing by selector")
        try:
            self.getElementByCSS(selector=selector).send_keys(value)
        
        except Exception as e:
            raise Exception("failed to text input to by selector ({}) due to: {}".format(selector, e))


    @__check_dry_run
    def select(self, selector: str, value: str) -> None:
        print("executing select dropdown")
        try:
            print("attempt to select by visible text")
            element = self.getElementByCSS(selector=selector)
            select_element = Select(webelement=element)
            select_element.select_by_visible_text(text=value)
        
        except Exception as e:
            print("failed to select ({})-({}) due to: {}".format(selector, value, e))
            print("attempt to select by value")
            select_element.select_by_value(value=value)

    
    @__check_dry_run
    def executeScript(self, script: str):
        self.driver.execute_script(script=script)


    @__check_dry_run
    def close(self):
        # self.driver.close() # this only close 1 tab.
        self.driver.quit()


    @__check_dry_run
    def highLightElements(self, elements: List[WebElement]):
        if not self.high_light_mode:
            return
        
        def moveToView(element: WebElement):
            self.driver.execute_script("arguments[0].scrollIntoView();", element)

        def applyStyle(element: WebElement, style: str):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, style)
        
        for element in elements:
            original_style = element.get_attribute('style')
            moveToView(element=element)
            applyStyle(element=element, style="border: {}px solid {};".format(HIGHLIGHT_ELEMENT_BORDER, HIGHLIGHT_ELEMENT_COLOR))
            time.sleep(HIGHLIGHT_ELEMENT_DURATION)
            applyStyle(element=element, style=original_style)
