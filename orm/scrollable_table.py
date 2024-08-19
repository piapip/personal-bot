import tkinter as tk
from tkinter import ttk
from typing import List, Callable
import threading

from orm.driver import Driver
from orm.actions_history import (
    ActionType,
    Action,
)
from helpers.ui import StyledEntry
from configs.ui_configs import (
    ResultText
)

class TableHeader:
    def __init__(self, text: str, weight: int) -> None:
        self.text = text
        self.weight = weight


class HistoryActionRow:
    def __init__(
            self,
            master: tk.Frame,
            driver: Driver,
            action: Action,
            action_index: int,
            result_label: tk.Label,
            onDelete: Callable[[Action], None],
        ) -> None:
        """
        Calling ActionRow will do create an instance of ActionRow, also render it on the screen.

        :action_index: int: the index of the ACTION (not the row) in the entire history.
        :action_index: is only here as a relative value compared to other row to decide the showing order.
        :action_index: should not be used for any serious logic.
        :result_label: tk.Label: the label where the action shows the automation result.
        :driver: orm.driver.Driver: the browser where the automation will be executed.
        :onDelete: is the function that will be executed when the row is deleted.
        """
        self.master: tk.Frame = master
        self.driver: Driver = driver
        self.action_index: int = action_index
        self.action: Action = action
        self.result_label: tk.Label = result_label
        self.onDeleteCallback: Callable[[Action], None] = onDelete

        # I intentionally keep the cell separately instead of grouping them under the same widget
        # so I have rooms for customization if needed to.
        # I have no concrete design after all.

        # Replay button
        self.replay_button: tk.Button = tk.Button(master=master, text="Run", anchor=tk.W, command=self.retriggerHistoryAction)
        self.replay_button.grid(row=action_index+1, column=0, sticky=tk.E + tk.W)

        # Action cell.
        options=(
            ActionType.CLICK_BY_NAME,
            ActionType.CLICK_BY_SELECTOR,
            ActionType.CLICK_BY_VALUE,
            # ActionType.SWITCH_TAB,
        )

        self.selected_option = tk.StringVar()
        self.selected_option.set(action.action_type)
        self.option_menu = tk.OptionMenu(master, self.selected_option, *options, command=self.__onUpdateHistoryActionType)
        self.option_menu.grid(row=action_index+1, column=1, sticky=tk.E + tk.W)

        # Name cell.
        self.name_entry: ttk.Entry = StyledEntry(master=master)
        self.name_entry.grid(row=action_index+1, column=2, sticky=tk.E + tk.W)
        self.name_entry.insert(tk.END, action.name) # Fill data
        if not action.needName(): # Then check if I need to disable the entry
            self.name_entry.config(state="readonly")

        # CSS Selector cell.
        self.css_selector_entry: ttk.Entry = StyledEntry(master=master)
        self.css_selector_entry.grid(row=action_index+1, column=3, sticky=tk.E + tk.W)
        self.css_selector_entry.insert(tk.END, action.css) # Fill data
        if not action.needCSS(): # Then check if I need to disable the entry
            self.css_selector_entry.config(state="readonly")

        # Value cell.
        self.value_entry: ttk.Entry = StyledEntry(master=master)
        self.value_entry.grid(row=action_index+1, column=4, sticky=tk.E + tk.W)
        self.value_entry.insert(tk.END, action.value) # Fill data
        if not action.needValue(): # Then check if I need to disable the entry
            self.value_entry.config(state="readonly")

        # Remove button cell.
        self.remove_button: tk.Button = tk.Button(master=master, text="Remove", anchor=tk.W, command=self.__delete)
        self.remove_button.grid(row=action_index+1, column=5, sticky=tk.E + tk.W)


    # updateAction updates its own content based on the content provided via the GUI.
    # updateAction will remove the action's failed reason if there's any change to the action.
    def updateAction(self) -> None:
        has_new_change: bool = False

        new_name = self.name_entry.get()
        current_name = self.action.name
        if new_name != current_name:
            print("new name!")
            self.action.name = new_name
            has_new_change = True
        
        new_css_selector = self.css_selector_entry.get()
        if new_css_selector != self.action.css:
            print("new css!")
            self.action.css = new_css_selector
            has_new_change = True

        new_value = self.value_entry.get()
        if new_value != self.action.value:
            print("new value!")
            self.action.value = new_value
            has_new_change = True
        
        if has_new_change:
            # Reset the previous attempt's failed reason if the action has any change.
            self.action.failed_reason = "not execute yet!"


    def retriggerHistoryAction(self) -> None:
        """retriggerHistoryAction triggered the action that was executed from the past.
        It will also save the retrigger attempt as the latest version in the history.
        """
        self.updateAction()

        # Block the execute button to prevent double clicking.
        self.replay_button.config(state="disabled")
        
        # Update the result bar to yellow hinting that it's running. 
        self.result_label.configure(background="#f3e96c", text=ResultText.IN_PROGRESS)

        def __processHistoryAction():
            try:
                self.action.executeAction(driver=self.driver)
            except Exception as e:
                # Update the result label with error if there's an error
                self.result_label.configure(background="#f13c1c", text=ResultText.FAILED.format(e))
            else:
                # Else, mark it as done.
                self.result_label.configure(background="#3af40d", text=ResultText.SUCCESS)
            finally:
                self.replay_button.config(state="normal")
                # print("stored action: {}".format(self.history_actions[action_index]))

        # Put the long process of the browser trying to do stuff in the thread. 
        execution_thread = threading.Thread(target=__processHistoryAction)
        execution_thread.start()


    def __onUpdateHistoryActionType(self, action_type: str):
        """onUpdateHistoryActionType updates the history action's action_type
        and re-render the data blurring."""
        self.action.action_type = action_type

        # Disable all the entries of the row.
        self.name_entry.config(state="readonly")
        self.css_selector_entry.config(state="readonly")
        self.value_entry.config(state="readonly")

        # Then enable those that are required for the action type.
        match action_type:
            case ActionType.CLICK_BY_NAME:
                self.name_entry.configure(state="normal", background="white")
            case ActionType.CLICK_BY_SELECTOR:
                self.css_selector_entry.configure(state="normal", background="white")
            case ActionType.CLICK_BY_VALUE:
                self.css_selector_entry.configure(state="normal", background="white")
                self.value_entry.configure(state="normal", background="white")


    def __delete(self) -> None:
        """__delete deletes the row in the History and remove it from the saved data.
        """
        # TODO [13]: Put all of this under a frame or smt.
        # Like a widget, so if I want to delete the entire row,
        # I just need to call 1 "row.destroy()" instead of component one by one.
        # Though I don't hate this one by one, easy for customization.
    
        # Destroy all the widgets in the row.
        # TODO [13]: Put all of this under a frame or smt.
        self.replay_button.destroy()
        self.option_menu.destroy()
        self.name_entry.destroy()
        self.css_selector_entry.destroy()
        self.value_entry.destroy()
        self.remove_button.destroy()

        # Perform any necessary callback like removing data from the history list.
        self.onDeleteCallback(self.action)

class ScrollableActionTable:
    def __init__(self, master: tk.Frame, driver: Driver) -> None:
        self.master = master
        self.driver = driver
        self.headers: list[TableHeader] = []
        self.rows: list[HistoryActionRow] = []

        # Initiating the canvas for the scrollable table.
        self.main_canvas: tk.Canvas = tk.Canvas(master=master)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Link a scrollbar to the canvas.
        vertical_scroll_bar: tk.Scrollbar = tk.Scrollbar(master=master, orient=tk.VERTICAL, command=self.main_canvas.yview)
        vertical_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_canvas.configure(yscrollcommand=vertical_scroll_bar.set)

        # This is the main frame for the table, we'll be playing with the table's cell here.
        # Handling the table slot by slot provides more customization. 
        # I have no design so I prefer customization to code cleanliness for now. :3
        self.history_table_frame: ttk.Frame = ttk.Frame(master=self.main_canvas)
        self.history_table_frame_canvas_id: int = self.main_canvas.create_window((0, 0), window=self.history_table_frame, anchor=tk.N+tk.W)

        # Make the thing scale with the windows screen dynamically.
        self.history_table_frame.bind("<Configure>", self.__onFrameConfigure)
        self.main_canvas.bind("<Configure>", self.__updateCanvansFrameWidth)

    # setHeaders renders the table header.
    def setHeaders(self, headers: List[TableHeader]) -> None:
        self.headers = headers

        for i in range(len(headers)):
            header = headers[i]
            self.history_table_frame.grid_columnconfigure(index=i, weight=header.weight)
            tk.Label(master=self.history_table_frame, text=header.text, anchor=tk.W).grid(row=0, column=i, sticky=tk.N + tk.E + tk.W + tk.S)


    # addHistoryActionRow adds an action row to the list.
    # It will also render the row to the screen.
    def addHistoryActionRow(
            self,
            action: Action,
            result_label: tk.Label,
            onDelete: Callable[[Action], None],
        ):
        """
        :result_label: tk.Label: the label where the action shows the automation result.
        :onDelete: is the function that will be executed when the row is deleted.
        """
        action_row = HistoryActionRow(
            master=self.history_table_frame,
            action=action,
            action_index=len(self.rows),
            driver=self.driver,
            result_label=result_label,
            onDelete=onDelete,
        )

        self.rows.append(action_row)


    # __updateCanvansFrameWidth makes the table's size scale with the window's resizing. 
    # https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas
    def __updateCanvansFrameWidth(self, event: tk.Event):
        canvas_width = event.width
        self.main_canvas.itemconfig(self.history_table_frame_canvas_id, width=canvas_width)

    # __onFrameConfigure updates the canvas's coverage on window resizing.
    # https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas
    def __onFrameConfigure(self, event: tk.Event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
