from tkinter import Tk, ttk 
import tkinter as tk
from typing import Dict

from configs.ui_configs import (
    GUI_SIZE,
    ACTION_TAB_KEY,
    HISTORY_TAB_KEY,
)
from orm.driver import Driver
from orm.scrollable_table import (
    ScrollableActionTable,
)
from orm.tab_templates import TabTemplates
from helpers.ui import (
    SetStyle,
)

class UI:
    def __init__(self, driver:Driver) -> None:
        self.driver = driver
        self.root = Tk()
        SetStyle()

        self.root.geometry(newGeometry=GUI_SIZE)
        self.root.title(string="Execute window")
        self.frames: Dict[str, tk.Frame] = {}

        tab_control = ttk.Notebook(master=self.root)
        tab_control.pack(expand=1, fill="both")
        self.tab_control = tab_control
        
        # Tab 1 for the action (Deleted, can be replaced with something else)
        self.__renderActionTab()
        
        # Tab 2 for the history (Deleted, can be replaced with something else)
        self.__renderHistoryTab()

        # Tab 3 for the templates for repetitive automation.
        self.__renderTemplateTab()
        
        tab_control.select(self.tab_templates.main_ui)
    

    # __renderActionTab generates the tab for performing actions on the automation browser. 
    def __renderActionTab(self) -> None:
        action_tab = ttk.Frame(master=self.tab_control)
        self.frames[ACTION_TAB_KEY] = action_tab
        
        tk.Label(master=action_tab, height=1, padx=10, pady=10, text="This UI is deleted.").pack(padx=10, pady=10, fill="x")
        
        self.tab_control.add(child=action_tab, text="Actions")

    # __renderHistoryTab generates the tab containing 
    # all the actions that were executed in the "Actions" tab.
    # Process:
    # 1. Initiate the main frame including:
    #    1.1. the tab's Header (not table header): Save button.
    #    1.2. Main content: The table and the scroll bar.
    #    1.3. Footer: The result label.
    # 2. Fill in the table data.
    #    2.1. Start with the header.
    #    2.2. Fill up the actions.
    def __renderHistoryTab(self) -> None:        
        history_tab = ttk.Frame(master=self.tab_control)
        self.frames[HISTORY_TAB_KEY] = history_tab

        tk.Label(master=history_tab, height=1, padx=10, pady=10, text="This UI is deleted.").pack(padx=10, pady=10, fill="x")

        self.tab_control.add(child=history_tab, text="History")


    def __renderTemplateTab(self) -> None:
        self.tab_templates: TabTemplates = TabTemplates(master=self.tab_control, driver=self.driver)
        self.tab_control.add(child=self.tab_templates.main_ui, text="Templates")


    # Start the application.
    def go(self) -> None:
        # When the UI is initiated, it's linked to the mock browser, but not linked to any tab yet.
        # The mock browser always has 1 empty tab open, so for convenience, I'll link the UI to that empty tab.
        self.driver.switchTab(0)
        self.root.mainloop()
