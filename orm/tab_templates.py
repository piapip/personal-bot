from tkinter import ttk, simpledialog
import tkinter as tk
import threading

from orm.driver import Driver
from orm.actions_history import (
    ActionType,
    Action,
)
from orm.scrollable_table import (
    TableHeader,
    ScrollableActionTable,
)

from helpers.action import sleep

class Template:
    def __init__(self, master: ttk.Notebook, driver: Driver) -> None:
        self.master: ttk.Notebook = master
        self.name: str = "New template"
        self.driver: Driver = driver

        # self.actions: list[Action] = [
        #     Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
        #     # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        # ]
        
        self.main_ui: tk.Frame = tk.Frame(master=master)
        # The default content of the template tab.
        # The layout would be:
        #   1. Header: The result label.
        #      The template can be looped over and over for a very long time,
        #      so I need to keep myself up to date about the processing of each template,
        #      therefore, it would be to the top, and each template will have its own result_label.
        #   2. Middle part containing all the actions.
        #      2.1. Start with the header.
        #      2.2. Fill up the actions.

        # Initiate top and the middle part.
        # Just in case, this Template's top_frame and middle_frame is 
        # not similar to the TabTemplate's top_frame and middle_frame. 
        self.top_frame: tk.Frame = tk.Frame(master=self.main_ui)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.middle_frame: tk.Frame = tk.Frame(master=self.main_ui)
        self.middle_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)        

        # [1]
        self.result_label: tk.Label = tk.Label(master=self.top_frame, background="#e5e0df", height=1, padx=10, pady=10, text="Waiting for command")
        self.result_label.pack(padx=10, pady=10, fill="x")

        # [2]
        # Now actually filling in the table of the middle_frame.
        self.action_table: ScrollableActionTable = ScrollableActionTable(
            master=self.middle_frame,
            driver=self.driver,
            result_label=self.result_label,
            enable_add_row_button=True)

        # [2.1.]
        # Start with the header.
        headers: list[TableHeader] = [
            TableHeader(text="", weight=1),                # Column for the play button.
            TableHeader(text="Action", weight=1),          # Column for the action.
            TableHeader(text="Name", weight=4),            #
            TableHeader(text="CSS Selector", weight=4),    #
            TableHeader(text="Value", weight=4),           #
            TableHeader(text="", weight=1),                # Column for the Remove button.
        ]

        self.action_table.setHeaders(headers=headers)

        # [2.2.]
        # Then fill up the actions.
        # Render the list of the actions to the table.

        # for action in self.actions:
        #     self.action_table.addHistoryActionRow(action=action)
    
    
    # run_all executes all the actions of the template one by one.
    def run_all(self) -> None:
        # Maybe add some progress bar above.
        execution_thread = threading.Thread(target=self.action_table.retriggerAll)
        execution_thread.start()
            

class TabTemplates:
    def __init__(self, master: ttk.Notebook, driver: Driver) -> None:
        self.master: ttk.Notebook = master
        self.driver: Driver = driver

        # main_ui contains everything of this tab.
        self.main_ui = tk.Frame(master=master)
        # templates contains all the templates that this tab is showing.
        self.templates: list[Template] = []

        # Separaate the main_ui of this tab into 2 parts:
        # [1] Top part containing options like Save, Save All, Rename, ...
        # [2] The middle part containing the templates which is also a bunch of tabs.
        #     So tabs in tabs.
        self.top_frame: tk.Frame = tk.Frame(master=self.main_ui)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.middle_frame: tk.Frame = tk.Frame(master=self.main_ui)
        self.middle_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # [1] Set up buttons for the top_frame.
        self.save_button = tk.Button(master=self.top_frame, text="Run all", width="6", command=self.__runAll)
        self.save_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(master=self.top_frame, text="Save", width="6")
        self.save_button.pack(side=tk.LEFT)

        self.save_all_button = tk.Button(master=self.top_frame, text="Save all", width="6")
        self.save_all_button.pack(side=tk.LEFT)

        # TODO [11]: Add a hotkey for this?
        self.rename_button = tk.Button(master=self.top_frame, text="Rename", width="6", command=self.__onRenameTab)
        self.rename_button.pack(side=tk.LEFT)

        self.import_button = tk.Button(master=self.top_frame, text="Import", width="6")
        self.import_button.pack(side=tk.RIGHT)

        self.export_button = tk.Button(master=self.top_frame, text="Export", width="6")
        self.export_button.pack(side=tk.RIGHT)

        # [2] Setup the template zone for the middle_frame.
        self.template_tabs_control: ttk.Notebook = ttk.Notebook(master=self.main_ui, padding=(0, 4, 0, 0))
        self.template_tabs_control.pack(expand=1, fill="both")

        # For the middle_frame that includes templates, initiate with
        #   [2.1.] an empty template
        #   [2.2.] a "add new template" button,
        # like how we do in the browser.
        
        # [2.1.]
        starting_template: Template = Template(master=self.template_tabs_control, driver=self.driver)
        self.template_tabs_control.add(child=starting_template.main_ui, text=starting_template.name)
        self.templates.append(starting_template)

        # [2.2.] https://stackoverflow.com/questions/71859022/tkinter-notebook-create-new-tabs-by-clicking-on-a-plus-tab-like-every-web-brow
        self.template_tabs_control.bind(sequence="<<NotebookTabChanged>>", func=self.__onAddTabClick)
        add_new_tab_button = tk.Frame()
        self.template_tabs_control.add(child=add_new_tab_button, text="+")


    # __onRenameTab asks the end user to provide the new name for the current selected tab,
    # then rename the current selected tab.
    # If the end user provides nothing, or cancel the prompt, then do nothing.
    def __onRenameTab(self) -> None:
        response = simpledialog.askstring(
            title="New tab name",
            prompt="Please enter the tab name").strip()
        if response is not None and response != "":
            self.template_tabs_control.tab(self.template_tabs_control.select(), text=response)

    
    # __onAddTabClick checked if the users click on the <<New tab icon>> (aka the last tab).
    # If they do, add a new tab right before the <<New tab icon>>,
    # and select that newly added tab.
    # https://stackoverflow.com/questions/71859022/tkinter-notebook-create-new-tabs-by-clicking-on-a-plus-tab-like-every-web-brow
    # 
    # TODO [12]: Add a hotkey for this?
    def __onAddTabClick(self, _: tk.Event) -> None:
        # tk.Frame is the Template.main_ui
        selected_tab: tk.Frame = self.template_tabs_control.select()
        new_tab_icon: tk.Frame = self.template_tabs_control.tabs()[-1]
        
        if selected_tab == new_tab_icon:
            index = len(self.template_tabs_control.tabs()) - 1
            new_template = Template(master=self.template_tabs_control, driver=self.driver)
            self.template_tabs_control.insert(index, child=new_template.main_ui, text=new_template.name)
            self.template_tabs_control.select(index)
            self.templates.append(new_template)

    
    # __runAll run all the actions of the selected template.
    def __runAll(self) -> None:
        current_tab_index: int = self.template_tabs_control.index(self.template_tabs_control.select())
        print("current_tab_index: ", current_tab_index)
        current_template = self.templates[current_tab_index]
        current_template.run_all()
