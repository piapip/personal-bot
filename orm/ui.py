from tkinter import Tk, ttk, messagebox 
import tkinter as tk
from typing import Dict
from configs.ui_configs import (
    GUI_SIZE,
    ACTION_TAB_KEY,
    HISTORY_TAB_KEY,
    HISTORY_TABLE_KEY,
    NAME_ENTRY_KEY,
    CSS_SELECTOR_ENTRY_KEY,
    VALUE_ENTRY_KEY,
    TAB_INDEX_KEY,
    ACTION_OPTION_BOX_KEY,
    SINGLE_ACTION_RESULT_KEY,
    HISTORY_ACTION_RESULT_KEY,
    FOOTER_GRID_ROW,
    ResultText,
    HISTORY_TABLE_KEY,
    EXECUTE_BUTTON_KEY,
)
from orm.driver import Driver
from orm.actions_history import (
    ActionType,
    Action,
)
import threading


ENTRY_LABELS = [
    NAME_ENTRY_KEY,
    CSS_SELECTOR_ENTRY_KEY,
    VALUE_ENTRY_KEY,
    TAB_INDEX_KEY,
]

class UI:
    def __init__(self, driver:Driver) -> None:
        self.driver = driver
        self.root = Tk()
        # Set style for the Entry, to make the text having some type of padding.
        ttk.Style().configure('pad.TEntry', padding='5 3 3 3 ')

        self.root.geometry(newGeometry=GUI_SIZE)
        self.root.title(string="Execute window")
        self.frames: Dict[str, tk.Frame] = {}
        self.entries: Dict[str, tk.Entry] = {}
        self.selected_option_boxes: Dict[str, str] = {}
        self.result_labels: Dict[str, tk.Label] = {}
        self.buttons: Dict[str, tk.Button] = {}
        self.history_actions: list[Action] = [
            Action(action_type=ActionType.CLICK_BY_NAME, name="name 1", css="", value="", tab_index=0),
            Action(action_type=ActionType.CLICK_BY_VALUE, name="", css="css2", value="value 2", tab_index=0),
            Action(action_type=ActionType.CLICK_BY_SELECTOR, name="", css="css3", value="", tab_index=0),
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

        tab_control = ttk.Notebook(master=self.root)
        tab_control.pack(expand=1, fill="both")
        self.tab_control = tab_control
        
        # Tab 1 for the action
        self.__renderActionTab()
        
        # Tab 2 for the history
        self.__renderHistoryActionsTab()
        
        tab_control.select(self.frames[HISTORY_TAB_KEY])

    
    def Entry(self, master: tk.Frame) -> ttk.Entry:
        return ttk.Entry(master=master, style="pad.TEntry")
    

    def addTextInput(self, master_label:str, answer_label:str, text:str, disabled:bool):
        master = self.frames[master_label]
        
        # Match the ratio of the addOptionBox function.
        entry_label_frame = tk.Frame(master=master)
        entry_label_frame.columnconfigure(index=0, weight=2, uniform="tag")
        entry_label_frame.columnconfigure(index=1, weight=6, uniform="tag")
        entry_label_frame.columnconfigure(index=2, weight=2, uniform="tag")
        
        label = tk.Label(master=entry_label_frame, text=text, width=12, anchor=tk.W)
        label.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        entry = self.Entry(master=entry_label_frame)
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

    
    def __addHistoryActionRow(self, action: Action, action_index: int) -> None:
        """__addHistoryActionRow render the rows to represent
        the executed action on the Actions History table.
        """
        history_table = self.frames[HISTORY_TABLE_KEY]

        replay_button = tk.Button(master=history_table, text="Run", anchor=tk.W)
        replay_button.grid(row=action_index+1, column=0, sticky=tk.E + tk.W)
    
        # Name column
        name_entry = self.Entry(master=history_table)
        name_entry.grid(row=action_index+1, column=2, sticky=tk.E + tk.W)
        name_entry.insert(tk.END, action.name) # Fill data
        if not action.needName(): # Then check if I need to disable the entry
            name_entry.config(state="readonly")
        
        # CSS Selector column
        css_selector_entry = self.Entry(master=history_table)
        css_selector_entry.grid(row=action_index+1, column=3, sticky=tk.E + tk.W)
        css_selector_entry.insert(tk.END, action.css) # Fill data
        if not action.needCSS(): # Then check if I need to disable the entry
            css_selector_entry.config(state="readonly")

        # Value column
        value_entry = self.Entry(master=history_table)
        value_entry.grid(row=action_index+1, column=4, sticky=tk.E + tk.W)
        value_entry.insert(tk.END, action.value) # Fill data
        if not action.needValue(): # Then check if I need to disable the entry
            value_entry.config(state="readonly")

        def __retriggerHistoryAction(replay_button=replay_button) -> None:
            """__retriggerHistoryAction triggered the action that was executed from the past.
            It will also save the retrigger attempt as the latest version in the history.
            """
            result_label = self.result_labels[HISTORY_ACTION_RESULT_KEY]
            action.name = name_entry.get()
            action.css = css_selector_entry.get()
            action.value = value_entry.get()
            action.failed_reason = "" # Reset the previous attempt's failed reason as well.

            # Block the execute button to prevent double clicking.
            replay_button.config(state="disabled")
            
            # Update the result bar to yellow hinting that it's running. 
            result_label.configure(background="#f3e96c", text=ResultText.IN_PROGRESS)

            def __processHistoryAction():
                try:
                    self.executeAction(action)
                except Exception as e:
                    # Update the result label with error if there's an error
                    result_label.configure(background="#f13c1c", text=ResultText.FAILED.format(e))
                else:
                    # Else, mark it as done.
                    result_label.configure(background="#3af40d", text=ResultText.SUCCESS)
                finally:
                    replay_button.config(state="normal")
                    print("stored action: {}".format(self.history_actions[action_index]))

            # Put the long process of the browser trying to do stuff in the thread. 
            execution_thread = threading.Thread(target=__processHistoryAction)
            execution_thread.start()

        # Replay button column
        replay_button.config(command=__retriggerHistoryAction)

        def onUpdateHistoryActionType(action_type: str):
            """onUpdateHistoryActionType updates the history action's action_type
            and re-render the data blurring."""
            action.action_type = action_type

            # Disable all the entries of the row.
            name_entry.config(state="readonly")
            css_selector_entry.config(state="readonly")
            value_entry.config(state="readonly")

            # Then enable those that are required for the action type.
            match action_type:
                case ActionType.CLICK_BY_NAME:
                    name_entry.configure(state="normal", background="white")
                case ActionType.CLICK_BY_SELECTOR:
                    css_selector_entry.configure(state="normal", background="white")
                case ActionType.CLICK_BY_VALUE:
                    css_selector_entry.configure(state="normal", background="white")
                    value_entry.configure(state="normal", background="white")
        
        # Action column.
        # Even though, action column appears before the other entry columns,
        # due to the technical limitation that prevent us from updating the OptionBox's command,
        # I have to create the OptionBox last, because the command on update relies on having other columns initiated first.
        options=(
            ActionType.CLICK_BY_NAME,
            ActionType.CLICK_BY_SELECTOR,
            ActionType.CLICK_BY_VALUE,
            # ActionType.SWITCH_TAB,
        )

        selected_option = tk.StringVar()
        selected_option.set(action.action_type)
        option_menu = tk.OptionMenu(history_table, selected_option, *options, command=onUpdateHistoryActionType)
        option_menu.grid(row=action_index+1, column=1, sticky=tk.E + tk.W)
            
        # Replay button column
        # TODO [4]: Enable remove line option.
        remove_button = tk.Button(master=history_table, text="Remove", anchor=tk.W)
        remove_button.grid(row=action_index+1, column=5, sticky=tk.E + tk.W)
    

    def __renderHistoryActionsTab(self) -> None:
        """__renderHistoryActionsTab generates the tab containing 
        all the actions that were executed in the "Actions" tab.
        """
        
        history_tab = ttk.Frame(master=self.tab_control)
        self.frames[HISTORY_TAB_KEY] = history_tab

        # Outer grid: 2 column: 1 for the big canvas, 1 for the scrollbar.
        main_canvas = tk.Canvas(master=history_tab)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Link a scrollbar to the canvas.
        vertical_scroll_bar = tk.Scrollbar(master=history_tab, orient=tk.VERTICAL, command=main_canvas.yview)
        vertical_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        main_canvas.configure(yscrollcommand=vertical_scroll_bar.set)
        
        # The actual frame that contains the history that we'll work with mainly.
        history_table_frame = ttk.Frame(master=main_canvas)
        canvas_frame = main_canvas.create_window((0, 0), window=history_table_frame, anchor=tk.N+tk.W)

        # Events to make the table scale with the window's resizing. 
        def updateCanvansFrameWidth(event: tk.Event):
            canvas_width = event.width
            main_canvas.itemconfig(canvas_frame, width=canvas_width)

        def onFrameConfigure(event: tk.Event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))

        history_table_frame.bind("<Configure>", onFrameConfigure)
        main_canvas.bind("<Configure>", updateCanvansFrameWidth)

        self.frames[HISTORY_TABLE_KEY] = history_table_frame

        class Header:
            def __init__(self, text: str, weight: int) -> None:
                self.text = text
                self.weight = weight

        headers: list[Header] = [
            Header(text="", weight=1),                # Column for the play button.
            Header(text="Action", weight=1),          # Column for the action.
            Header(text="Name", weight=4),            #
            Header(text="CSS Selector", weight=4),    #
            Header(text="Value", weight=4),           #
            Header(text="", weight=1),                # Column for the Remove button.
        ]

        # Render the table header.
        for i in range(len(headers)):
            header = headers[i]
            history_table_frame.grid_columnconfigure(index=i, weight=header.weight)
            tk.Label(master=history_table_frame, text=header.text, anchor=tk.W).grid(row=0, column=i, sticky=tk.N + tk.E + tk.W + tk.S)
        
        # Render the list of the actions to the table.
        for i in range(len(self.history_actions)):
            # Closure problem with python.
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
            # By calling __addHistoryActionRow with all the parameter name defined,
            # I accidentally lock the i value without knowing :3
            self.__addHistoryActionRow(action=self.history_actions[i], action_index=i)

        result_label = tk.Label(master=history_table_frame, background="#e5e0df", height=1, padx=10, pady=10, text="Waiting for command")
        result_label.grid(pady=10, column=0, row=FOOTER_GRID_ROW, columnspan=len(headers), sticky=tk.E + tk.W)
        self.result_labels[HISTORY_ACTION_RESULT_KEY] = result_label
        
        # TODO [3]: - Add save(export)/import option for the Actions History tab.
        self.tab_control.add(child=history_tab, text="Actions History")


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


    # executeAction executes the given command on the driver based on the given action type.
    # It's expected for this action to take a long time to execute,
    # so remember to use thread to call this function.
    def executeAction(self, action: Action) -> None:
        from helpers.action import sleep

        sleep(1.5)

        try:
            match action.action_type:
                case ActionType.CLICK_BY_NAME:
                    # raise Exception("forced fail")
                    if action.name == "":
                        raise Exception("name is expected for the Click by Name action")
                    else:
                        self.driver.clickByName(name=action.name)
                case ActionType.CLICK_BY_SELECTOR:
                    css_selector = action.css
                    
                    if css_selector == "":
                        raise Exception("css_selector is expected for the Click by CSS action")
                    else:
                        self.driver.clickByCSS(selector=css_selector)
                case ActionType.CLICK_BY_VALUE:
                    css_selector = action.css
                    value = action.value
                    
                    if css_selector == "" or value == "":
                        raise Exception("css_selector and value are expected for the Click by Value action")
                    else:
                        self.driver.clickByValue(selector=css_selector, value=value)
                    
                case ActionType.SWITCH_TAB:
                    self.driver.switchTab(tab_index=action.tab_index)
        except Exception as e:
            action.failed_reason = "{}".format(e)
            raise e
        finally:
            print("executed: {}".format(action))
        
        # If the action reaches to the end without any problem, then mark it as successful.
        action.failed_reason = ""
    
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

        action_index : int = 0
        if action.needToStore():
            action_index = len(self.history_actions)
            self.history_actions.append(action)

        # Update the result bar to yellow hinting that it's running. 
        result_label.configure(background="#f3e96c", text=ResultText.IN_PROGRESS)

        # Block the execute button to prevent double clicking.
        submit_button = self.buttons[EXECUTE_BUTTON_KEY]
        submit_button.config(state="disabled")

        def __processAction(action=action):
            try:
                self.executeAction(action=action)
            except Exception as e:
                # Update the result label with error if there's an error
                result_label.configure(background="#f13c1c", text=ResultText.FAILED.format(e))
            else:
                # Else, mark it as done.
                result_label.configure(background="#3af40d", text=ResultText.SUCCESS)
            finally:
                submit_button.config(state="normal")
                if action.needToStore():
                    self.__addHistoryActionRow(action=action, action_index=action_index)
        
        # Put the long process of the browser trying to do stuff in the thread. 
        execution_thread = threading.Thread(target=__processAction)
        execution_thread.start()
        

    # Start the application.
    def go(self) -> None:
        self.root.mainloop()
