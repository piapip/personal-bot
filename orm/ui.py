from tkinter import Tk, ttk, simpledialog 
import tkinter as tk
from typing import Dict
import threading
import re
import json
from pathlib import Path

from configs.ui_configs import (
    GUI_SIZE,
    ACTION_TAB_KEY,
    HISTORY_TAB_KEY,
    TEMPLATE_TAB_KEY,
    NAME_ENTRY_KEY,
    CSS_SELECTOR_ENTRY_KEY,
    VALUE_ENTRY_KEY,
    TAB_INDEX_KEY,
    ACTION_OPTION_BOX_KEY,
    SINGLE_ACTION_RESULT_KEY,
    HISTORY_ACTION_RESULT_KEY,
    ResultText,
    EXECUTE_BUTTON_KEY,
)
from orm.driver import Driver
from orm.actions_history import (
    ActionType,
    Action,
)
from orm.scrollable_table import (
    TableHeader,
    ScrollableActionTable,
)
from orm.tab_templates import TabTemplates
from helpers.ui import (
    StyledEntry,
    SetStyle,
)


ENTRY_LABELS = [
    NAME_ENTRY_KEY,
    CSS_SELECTOR_ENTRY_KEY,
    VALUE_ENTRY_KEY,
    TAB_INDEX_KEY,
]

class UI:
    def __init__(self, driver:Driver) -> None:
        # Make the history folder if not exists.
        self.history_folder = "./history"
        Path(self.history_folder).mkdir(parents=True, exist_ok=True)
        self.history_filename = "dump.json"
        self.save_file_name: str = self.history_folder + "/" + self.history_filename

        self.driver = driver
        self.root = Tk()
        SetStyle()

        self.root.geometry(newGeometry=GUI_SIZE)
        self.root.title(string="Execute window")
        self.frames: Dict[str, tk.Frame] = {}
        self.entries: Dict[str, tk.Entry] = {}
        self.selected_option_boxes: Dict[str, str] = {}
        self.result_labels: Dict[str, tk.Label] = {}
        self.buttons: Dict[str, tk.Button] = {}
        
        # TODO [14]: I can probably kill this thing?
        # It's already in the history and easily exportable.
        self.history_actions: list[Action] = [
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            # Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
        ]
        self.loadHistory()

        tab_control = ttk.Notebook(master=self.root)
        tab_control.pack(expand=1, fill="both")
        self.tab_control = tab_control
        
        # Tab 1 for the action
        self.__renderActionTab()
        
        # Tab 2 for the history
        self.__renderHistoryTab()

        # Tab 3 for the templates for repetitive automation.
        self.__renderTemplateTab()
        
        tab_control.select(self.tab_templates.main_ui)
    

    def addTextInput(self, master_label:str, answer_label:str, text:str, disabled:bool):
        master = self.frames[master_label]
        
        # Match the ratio of the addOptionBox function.
        entry_label_frame = tk.Frame(master=master)
        entry_label_frame.columnconfigure(index=0, weight=2, uniform="tag")
        entry_label_frame.columnconfigure(index=1, weight=6, uniform="tag")
        entry_label_frame.columnconfigure(index=2, weight=2, uniform="tag")
        
        label = tk.Label(master=entry_label_frame, text=text, width=12, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        entry = StyledEntry(master=entry_label_frame)
        entry.grid(row=0, column=1, sticky=tk.W + tk.E)
        if disabled:
            entry.config(state="readonly")
        entry_label_frame.pack(fill="x", padx=10, pady=10)
        master.pack(fill="x")
        # Remember the entry to extract the data from this entry later.
        self.entries[answer_label] = entry
        

    def addOptionBox(self) -> None:
        master = self.frames[ACTION_TAB_KEY]
        
        # Match the ratio of the addTextInput function.
        option_box_label_frame = tk.Frame(master=master)
        option_box_label_frame.columnconfigure(index=0, weight=2, uniform="tag")
        option_box_label_frame.columnconfigure(index=1, weight=6, uniform="tag")
        option_box_label_frame.columnconfigure(index=2, weight=2, uniform="tag")

        label = tk.Label(master=option_box_label_frame, text="Actions", width=12, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W + tk.E)

        options=(
            ActionType.CLICK_BY_NAME,
            ActionType.CLICK_BY_SELECTOR,
            ActionType.CLICK_BY_VALUE,
            ActionType.SWITCH_TAB,
        )
        
        selected_option = tk.StringVar()
        # Remember the entry to extract the data from this entry later.
        self.selected_option_boxes[ACTION_OPTION_BOX_KEY] = ""

        def updateSelectedOption(selection: str):
            self.selected_option_boxes[ACTION_OPTION_BOX_KEY] = selection
            self.__optionBoxRerender()

        # Python is a PoS if they can't express this clearly...
        option_menu = tk.OptionMenu(option_box_label_frame, selected_option, *options, command=updateSelectedOption)
        option_menu.configure(width=14)
        option_menu.grid(row=0, column=1, sticky=tk.W)
        option_box_label_frame.pack(fill="x", padx=10, pady=10)
        master.pack(fill="x")


    # __renderActionTab generates the tab for performing actions on the automation browser. 
    def __renderActionTab(self) -> None:
        action_tab = ttk.Frame(master=self.tab_control)
        self.frames[ACTION_TAB_KEY] = action_tab
        
        # Setup the option box to select Action
        # and re-render the UI when the Action is changed.
        self.addOptionBox()

        # Setup the textarea to fill in the input for the actions.
        self.addTextInput(master_label=ACTION_TAB_KEY, answer_label=NAME_ENTRY_KEY, text="Name", disabled=True)
        self.addTextInput(master_label=ACTION_TAB_KEY, answer_label=CSS_SELECTOR_ENTRY_KEY, text="CSS Selector", disabled=True)
        self.addTextInput(master_label=ACTION_TAB_KEY, answer_label=VALUE_ENTRY_KEY, text="Value", disabled=True)
        self.addTextInput(master_label=ACTION_TAB_KEY, answer_label=TAB_INDEX_KEY, text="Tab Index", disabled=True)
        
        result_label = tk.Label(master=action_tab, background="#e5e0df", height=1, padx=10, pady=10, text="Waiting for command")
        result_label.pack(padx=10, pady=10, fill="x")
        self.result_labels[SINGLE_ACTION_RESULT_KEY] = result_label

        # Add the submit button to run the Automation on the browser (aka driver).
        submit_button = tk.Button(master=action_tab, text="Execute", command=self.__submitButtonPressed)
        submit_button.pack()
        self.buttons[EXECUTE_BUTTON_KEY] = submit_button
        
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

        # Outer grid:
        #  Header: button to save the history.
        #  Main content: main screen for the big canvas, right side for the scrollbar.
        #  Footer: show the result label.

        # [1.] 
        # [1.3.] Footer
        # Initiate this first because the rest of the screen's error reporting will be via the footer banner.
        # We place it on the screen later though.
        result_label = tk.Label(master=history_tab, background="#e5e0df", height=1, padx=10, pady=10, text="Waiting for command")
        self.result_labels[HISTORY_ACTION_RESULT_KEY] = result_label
                
        # [1.1.] Header
        save_button = tk.Button(master=history_tab, text="Save", width="6")
        save_button.pack(anchor=tk.W)

        def onSave():
            save_button.config(state="disabled", text="Saving...")
            
            def savingProcess():
                try:
                    # TODO [16]: updateAction before saving. 
                    self.save()
                except Exception as e:
                    print("failed to save: {}".format(e))
                finally:
                    save_button.config(state="normal", text="Save")

            # Normally, this process is pretty fast. But hey, just to be sure.
            saving_thread = threading.Thread(target=savingProcess)
            saving_thread.start()

        save_button.config(command=onSave)

        # [1.2.] Main content
        main_content_frame = tk.Frame(master=history_tab)
        main_content_frame.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        
        # Placing the footer
        result_label.pack(padx=10, pady=10, fill="x")

        # [2.]
        # Now actually filling in the table of the main content.
        self.action_table: ScrollableActionTable = ScrollableActionTable(master=main_content_frame, driver=self.driver)
        
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
        for i in range(len(self.history_actions)):
            # Closure problem with python. [EXPLAIN]
            # If I ever need to lock this i value, like how Go used to do "i:=i"
            # This is how python locks value.
            # 
            # def run_action(i = i):
            #     try: 
            #         self.executeAction(self.history_actions[i])
            #     except Exception as e:
            #         print("Exception: {}".format(e))
            # 
            # If I do this instead:
            # 
            # def run_action():
            #     index = i
            #     self.executeAction(self.history_actions[i])
            # 
            # Then. the "index" will take "i"'s reference instead of the "i" current value,
            # and the click_me function would refer to the last item.
            # Go is fine with this value locking, but not Python.
            # (Go lock by make a new reference pointing taking the same value, by reinitiating the variable using ":=")
            # 
            # By calling addHistoryActionRow with all the parameter name defined,
            # I accidentally lock the i value without knowing :3
            # In the example, is the action that is locked.
            # action_table.addHistoryActionRow(..., action=self.history_actions[i], ...)
            self.action_table.addHistoryActionRow(
                action=self.history_actions[i],
                result_label=result_label,
                onDelete=self.remove_history_action,
            )

        # TODO [3]: - Add save(export)/import option for the History tab.
        self.tab_control.add(child=history_tab, text="History")


    def __renderTemplateTab(self) -> None:
        self.tab_templates: TabTemplates = TabTemplates(master=self.tab_control, driver=self.driver)
        self.tab_control.add(child=self.tab_templates.main_ui, text="Templates")

    
    def __disableAllEntriesActionsTab(self) -> None:
        """__disableAllEntries clears all the entries of the Actions tab
        and converts them to readonly mode.
        """
        for label in self.entries:
            entry = self.entries[label]
            entry.delete(0, tk.END)
            entry.configure(state="readonly", background="grey")


    # __enableInputOptionsActionsTab changes the state of the entries to normal.
    # If the entry currently doesn't have any data, fill in some default message.
    def __enableInputOptionsActionsTab(self, answer_label: str, default_text: str) -> None:
        entry = self.entries[answer_label]
        entry.configure(state="normal", background="white")

        # clear_default attempts to clear the default text of the Entry input.
        def clear_default(event: tk.Event):
            event_button: tk.Entry = event.widget
            event_button.delete(0, tk.END)
            event_button.unbind('<FocusIn>')

        entry.insert(index=0, string=default_text)
        entry.bind(sequence='<FocusIn>', func=clear_default)


    # __optionBoxRerender re-renders the entire "Actions" tab when the "Actions" dropdown is changed. 
    def __optionBoxRerender(self) -> None:
        selected_action = self.selected_option_boxes[ACTION_OPTION_BOX_KEY]
        self.__disableAllEntriesActionsTab()

        match selected_action:
            case ActionType.CLICK_BY_NAME:
                # For the "ClickByName" ActionType.
                # Affected inputs are:
                # - Name
                self.__enableInputOptionsActionsTab(answer_label=NAME_ENTRY_KEY, default_text="Input name please")
            case ActionType.CLICK_BY_SELECTOR:
                # For the "ClickByCSS" ActionType.
                # Affected inputs are:
                # - CSS_Selector
                self.__enableInputOptionsActionsTab(answer_label=CSS_SELECTOR_ENTRY_KEY, default_text="Input css selector please")
            case ActionType.CLICK_BY_VALUE:
                # For the "ClickByValue" ActionType.
                # Affected inputs are:
                # - CSS_Selector
                # - Value
                self.__enableInputOptionsActionsTab(answer_label=CSS_SELECTOR_ENTRY_KEY, default_text="Input css selector please")
                self.__enableInputOptionsActionsTab(answer_label=VALUE_ENTRY_KEY, default_text="Input value please")
            case ActionType.SWITCH_TAB:
                # For the "SwitchTab" ActionType.
                # Affected inputs are:
                # - TabIndex
                tab_count = self.driver.countTabs()
                if tab_count == None or tab_count == 0:
                    self.__enableInputOptionsActionsTab(TAB_INDEX_KEY, "No tab")
                else:
                    self.__enableInputOptionsActionsTab(TAB_INDEX_KEY, "[0-{}]".format(tab_count - 1))

    
    # __gatherSubmittedData aggregates all the data given via the "Actions" tab into 1 Action.
    def __gatherSubmittedData(self) -> Action:
        action_type = self.selected_option_boxes[ACTION_OPTION_BOX_KEY]
        if action_type == "":
            raise Exception("Please select an action first.")
        
        match action_type:
            case ActionType.CLICK_BY_NAME:
                return Action(
                    action_type=action_type,
                    name=self.entries[NAME_ENTRY_KEY].get(),
                    css="",
                    tab_index=0,
                    value="",
                )                
            case ActionType.CLICK_BY_SELECTOR:
                return Action(
                    action_type=action_type,
                    name="",
                    css=self.entries[CSS_SELECTOR_ENTRY_KEY].get(),
                    tab_index=0,
                    value="",
                )
            case ActionType.CLICK_BY_VALUE:
                return Action(
                    action_type=action_type,
                    name="",
                    css=self.entries[CSS_SELECTOR_ENTRY_KEY].get(),
                    tab_index=0,
                    value=self.entries[VALUE_ENTRY_KEY].get(),
                )
            case ActionType.SWITCH_TAB:
                tab_index = self.entries[TAB_INDEX_KEY].get()

                if tab_index.isdigit():
                    return Action(
                        action_type=action_type,
                        name="",
                        css="",
                        tab_index=int(tab_index),
                        value=self.entries[VALUE_ENTRY_KEY].get(),
                    )
                else:
                    raise Exception("Tab index must be a positive number for the Switching Tab action!")
    
    # __submitButtonPressed contains the logic when we submit the data for the "Actions" tab.
    # Performing simple action on the selenium driver (bot windows)
    def __submitButtonPressed(self) -> None:
        result_label = self.result_labels[SINGLE_ACTION_RESULT_KEY]
        
        action : Action
        try:
            action = self.__gatherSubmittedData()
        except Exception as e:
            # Update the result label with error if there's an error
            result_label.configure(background="#f13c1c", text=ResultText.FAILED.format(e))
            return

        if action.needToStore():
            self.history_actions.append(action)

        # Update the result bar to yellow hinting that it's running. 
        result_label.configure(background="#f3e96c", text=ResultText.IN_PROGRESS)

        # Block the execute button to prevent double clicking.
        submit_button = self.buttons[EXECUTE_BUTTON_KEY]
        submit_button.config(state="disabled")

        def __processAction(action=action):
            try:
                action.executeAction(driver=self.driver)
            except Exception as e:
                # Update the result label with error if there's an error
                result_label.configure(background="#f13c1c", text=ResultText.FAILED.format(e))
            else:
                # Else, mark it as done.
                result_label.configure(background="#3af40d", text=ResultText.SUCCESS)
            finally:
                submit_button.config(state="normal")
                if action.needToStore():
                    self.action_table.addHistoryActionRow(
                        action=action,
                        result_label=self.result_labels[HISTORY_ACTION_RESULT_KEY],
                        onDelete=self.remove_history_action,
                    )
        
        # Put the long process of the browser trying to do stuff in the thread. 
        execution_thread = threading.Thread(target=__processAction)
        execution_thread.start()
        

    # Start the application.
    def go(self) -> None:
        # When the UI is initiated, it's linked to the mock browser, but not linked to any tab yet.
        # The mock browser always has 1 empty tab open, so for convenience, I'll link the UI to that empty tab.
        self.driver.switchTab(0)
        self.root.mainloop()

    
    # save exports the history to json.
    def save(self) -> None:

        print("Saving...")
        
        # # The actual saving.
        # # Later 
        # if self.save_file_name == "":
        #     if not re.match("[A-Za-z0-9-_]+", self.history_filename):
        #         raise Exception("filename can only contains: alphabetical characters, numbers, -, _. Your filename: {}".format(filename))
        #     self.save_file_name = self.history_folder + "/" + self.history_filename
        
        with open(self.save_file_name, "w") as f:
            json.dump(self.history_actions, default=lambda o: o.encode(), indent=4, fp=f)

        print("Done...")
    

    # loadHistory loads the history stored in history/dump.json file.
    def loadHistory(self):
        with open(self.save_file_name, "r") as f:
            actions: list[dict] = json.load(f)

        # print("type: {} history data: {}".format(type(data[0]), data[0])) 
        for action in actions:
            self.history_actions.append(Action(**action))


    def remove_history_action(self, action:Action) -> None:
        self.history_actions.remove(action)
