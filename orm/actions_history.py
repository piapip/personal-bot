from enum import StrEnum
from typing import List

class ActionType(StrEnum):
    CLICK_BY_NAME = "Click by name"
    CLICK_BY_SELECTOR = "Click by selector"
    CLICK_BY_VALUE = "Click by value"
    SWITCH_TAB = "Switch tab"

class Action:
    def __init__(self, action_type:ActionType, name: str, css: str, value: str, tab_index: int) -> None:
        self.action_type = action_type
        self.name = name
        self.css = css
        self.value = value
        self.tab_index = tab_index

    
    def __str__(self) -> str:
        return "Action: {}\nName: {}\nCSS: {}\nValue: {}\n".format(
            self.action_type,
            self.name,
            self.css,
            self.value,
        )
    
    
    def needName(self) -> bool:
        """
        needName tell us if the current action needs Name or not.
        
        Currently, only the ClickByName action needs this data.
        """
        return self.action_type == ActionType.CLICK_BY_NAME
    

    def needCSS(self) -> bool:
        """
        needCSS tell us if the current action needs CSS or not.
    
        Currently, the ClickBySelector action and ClickByValue needs this data.
        """
        return self.action_type == ActionType.CLICK_BY_SELECTOR or self.action_type == ActionType.CLICK_BY_VALUE
    

    def needValue(self) -> bool:
        """
        needValue tell us if the current action needs Value or not.
        
        Currently, only the ClickByValue action needs this data.
        """
        return self.action_type == ActionType.CLICK_BY_VALUE
    

    def needTabIndex(self) -> bool:
        """
        needTabIndex tell us if the current action needs tab_index or not.
    
        Currently, only the SwitchTab action needs this data.
        """
        return self.action_type == ActionType.SWITCH_TAB


