from enum import StrEnum
from orm.driver import Driver
import time
# from uuid import uuid4, UUID

from configs.ui_configs import DEFAULT_FAILED_RESULT
from helpers.action import sleepWithLog

class ActionType(StrEnum):
    OLD_TEXT_INPUT = "Text input"
    OLD_CLICK_BY_NAME = "Click by name"
    OLD_CLICK_BY_SELECTOR = "Click by selector"
    OLD_CLICK_BY_VALUE = "Click by value"
    OLD_SELECT_DROPDOWN = "Select dropdown"
    OLD_SWITCH_TAB = "Switch tab"
    OLD_SLEEP = "Sleep"

    TEXT_INPUT = "Input"
    CLICK_BY_NAME = "Click by name"
    CLICK_BY_SELECTOR = "Click"
    CLICK_BY_VALUE = "Click by Value"
    SELECT_DROPDOWN = "Select"
    SWITCH_TAB = "Switch tab"
    SLEEP = "Wait"

class Action:
    def __init__(
            self,
            action_type:ActionType,
            name: str,
            css: str,
            html_attribute: str,
            value: str,
            # TODO: Make skippable togglable. 
            # Currently, skippable can be used by assigned manually in the json file.
            skippable: bool = False,
            # Normally, we don't need to provide failed_reason,
            # I need to initiate it so Python can translate from dict to class. 
            failed_reason: str = DEFAULT_FAILED_RESULT) -> None:
        # This __id will be used for differentiating rows.
        # The History tab's remove button performs removal by value.
        # So in case if there are 2 actions with identical values,
        # the first one in the history will be removed instead of the targeted action.
        # This may cause unexpected behavior later.
        # To prevent that, add the uuid for each row as the just-in-case solution.
        # 
        # Hmmm still, even if the 2 actions have the same content,
        # it seems like they are not truly similar because they are referred by different pointer.
        # So python remove function is actually smart enough to differentiate between the two without the need of the __id.
        # self.__id: UUID = uuid4()
        self.action_type: ActionType = action_type
        self.name: str = name
        self.css: str = css
        self.html_attribute: str = html_attribute
        self.value: str = value
        self.failed_reason: str = failed_reason
        self.skippable: bool = skippable

    
    def __str__(self) -> str:
        return "Action: {}\nName: {}\nCSS: {}\nHTML Attribute: {}\nValue: {}\nError: {}\n".format(
            self.action_type,
            self.name,
            self.css,
            self.html_attribute,
            self.value,
            self.failed_reason,
        )
    
    
    def needName(self) -> bool:
        """
        needName tells us if the current action needs Name or not.
        
        Currently, only the ClickByName action needs this data.
        """
        return self.action_type == ActionType.CLICK_BY_NAME
    

    def needCSS(self) -> bool:
        """
        needCSS tells us if the current action needs CSS or not.
        """
        return (self.action_type == ActionType.TEXT_INPUT or
                self.action_type == ActionType.CLICK_BY_SELECTOR or 
                self.action_type == ActionType.CLICK_BY_VALUE or
                self.action_type == ActionType.SELECT_DROPDOWN)
    

    def needValue(self) -> bool:
        """
        needValue tells us if the current action needs Value or not.
        """
        return (self.action_type == ActionType.TEXT_INPUT or
                self.action_type == ActionType.CLICK_BY_VALUE or
                self.action_type == ActionType.SLEEP or
                self.action_type == ActionType.SWITCH_TAB or
                self.action_type == ActionType.SELECT_DROPDOWN)
    

    def needHTMLAttribute(self) -> bool:
        """
        needHTMLAttribute tells us if the current action needs HTML Attribute or not.
        """
        return (self.action_type == ActionType.CLICK_BY_VALUE)


    def needToStore(self) -> bool:
        """
        needToStore tells us if we need to track the executed action or not.
        True is we need to.
        False is we don't need to.
        """
        return (self.action_type == ActionType.TEXT_INPUT or
                self.action_type == ActionType.CLICK_BY_SELECTOR or
                self.action_type == ActionType.CLICK_BY_VALUE or
                self.action_type == ActionType.SWITCH_TAB or
                self.action_type == ActionType.SELECT_DROPDOWN)


    def hasError(self) -> bool:
        """
        hasError tells us if the last attempt is 
        a successful attempt or a failed attempt. 
        """
        return self.failed_reason == ""
    

    # executeAction performs the automation action on the browser based on the action content.
    # It's expected for this action to take a long time to execute,
    # so remember to use thread to call this function.
    def executeAction(self, driver: Driver) -> None:
        if driver.dry_run:
            time.sleep(0.5)

        try:
            match self.action_type:
                case ActionType.TEXT_INPUT:
                    css_selector = self.css
                    value = self.value
                    
                    if css_selector == "" or value == "":
                        raise Exception("css_selector and value are expected for the Text Input action")
                    else:
                        driver.textInput(selector=css_selector, value=value)
                case ActionType.CLICK_BY_NAME:
                    # raise Exception("forced fail")
                    if self.name == "":
                        raise Exception("name is expected for the Click by Name action")
                    else:
                        driver.clickByName(name=self.name)
                case ActionType.CLICK_BY_SELECTOR:
                    css_selector = self.css
                    
                    if css_selector == "":
                        raise Exception("css_selector is expected for the Click by CSS action")
                    else:
                        driver.clickByCSS(selector=css_selector)
                case ActionType.CLICK_BY_VALUE:
                    css_selector = self.css
                    html_attribute = self.html_attribute
                    value = self.value
                    
                    if css_selector == "" or value == "":
                        raise Exception("css_selector and value are expected for the Click by Value action")
                    else:
                        if html_attribute != "":
                            driver.clickByAttribute(selector=css_selector, html_attribute=html_attribute, value=value)
                        else:
                            driver.clickByValue(selector=css_selector, value=value)
                case ActionType.SELECT_DROPDOWN:
                    css_selector = self.css
                    value = self.value
                    
                    if css_selector == "" or value == "":
                        raise Exception("css_selector and value are expected for the Select Dropdown action")
                    else:
                        driver.select(selector=css_selector, value=value)
                case ActionType.SWITCH_TAB:
                    if not self.value.isdigit():
                        raise Exception("value for switching tab must be a number")
                    driver.switchTab(tab_index=int(self.value))
                case ActionType.SLEEP:
                    sleepWithLog(duration=float(self.value))
        except Exception as e:
            self.failed_reason = "{}".format(e)
            if self.skippable:
                print("Got this error but skippable so ignore: {}".format(e))
            else:
                raise e
        else:
            self.failed_reason = ""
        finally:
            print("executed:\n{}".format(self))
        
        # If the action reaches to the end without any problem, then mark it as successful.
        self.failed_reason = ""


    # encode is for the UI's save feature, dumping data from class to JSON file.
    # https://stackoverflow.com/questions/61553988/json-serialization-of-a-list-of-objects-of-a-custom-class
    def encode(self):
        return self.__dict__


    # Update the new used in the app to match with the name in RPA.
    def updateName(self):
        match self.action_type:
            case ActionType.OLD_TEXT_INPUT:
                self.action_type = ActionType.TEXT_INPUT
            case ActionType.OLD_CLICK_BY_NAME:
                self.action_type = ActionType.CLICK_BY_NAME
            case ActionType.OLD_CLICK_BY_SELECTOR:
                self.action_type = ActionType.CLICK_BY_SELECTOR
            case ActionType.OLD_CLICK_BY_VALUE:
                self.action_type = ActionType.CLICK_BY_VALUE
            case ActionType.OLD_SELECT_DROPDOWN:
                self.action_type = ActionType.SELECT_DROPDOWN
            case ActionType.OLD_SWITCH_TAB:
                self.action_type = ActionType.SWITCH_TAB
            case ActionType.OLD_SLEEP:
                self.action_type = ActionType.SLEEP
