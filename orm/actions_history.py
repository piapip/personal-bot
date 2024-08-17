from enum import StrEnum
from uuid import uuid4, UUID

class ActionType(StrEnum):
    CLICK_BY_NAME = "Click by name"
    CLICK_BY_SELECTOR = "Click by selector"
    CLICK_BY_VALUE = "Click by value"
    SWITCH_TAB = "Switch tab"

class Action:
    def __init__(self, action_type:ActionType, name: str, css: str, value: str, tab_index: int) -> None:
        self.__id: UUID = uuid4()
        self.action_type: ActionType = action_type
        self.name: str = name
        self.css: str = css
        self.value: str = value
        self.tab_index: int = tab_index
        self.failed_reason: str = ""

    
    def __str__(self) -> str:
        return "Action: {}\nName: {}\nCSS: {}\nValue: {}\nError: {}\n".format(
            self.action_type,
            self.name,
            self.css,
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
    
        Currently, the ClickBySelector action and ClickByValue needs this data.
        """
        return (self.action_type == ActionType.CLICK_BY_SELECTOR or 
                self.action_type == ActionType.CLICK_BY_VALUE)
    

    def needValue(self) -> bool:
        """
        needValue tells us if the current action needs Value or not.
        
        Currently, only the ClickByValue action needs this data.
        """
        return self.action_type == ActionType.CLICK_BY_VALUE
    

    def needTabIndex(self) -> bool:
        """
        needTabIndex tells us if the current action needs tab_index or not.
    
        Currently, only the SwitchTab action needs this data.
        """
        return self.action_type == ActionType.SWITCH_TAB


    def needToStore(self) -> bool:
        """
        needToStore tells us if we need to track the executed action or not.
        True is we need to.
        False is we don't need to.
        """
        return (self.action_type == ActionType.CLICK_BY_NAME or
                self.action_type == ActionType.CLICK_BY_SELECTOR or
                self.action_type == ActionType.CLICK_BY_VALUE)


    def hasError(self) -> bool:
        """
        hasError tells us if the last attempt is 
        a successful attempt or a failed attempt. 
        """
        return self.failed_reason == ""
