import tkinter as tk
from tkinter import ttk
from typing import List, Callable
import threading
import json
import re

from orm.driver import Driver
from orm.actions_history import (
    ActionType,
    Action,
)
from helpers.ui import StyledEntry
from helpers.action import sleep
from configs.ui_configs import (
    ResultText,
    DEFAULT_FAILED_RESULT,
    IN_PROGRESS_BG_COLOR,
    FAILED_BG_COLOR,
    SUCCESS_BG_COLOR,
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
            onDeleteCallback: Callable[[Action], None],
        ) -> None:
        """
        Calling ActionRow will do create an instance of ActionRow, also render it on the screen.

        :action_index: int: the index of the ACTION (not the row) in the entire history.
        :action_index: is only here as a relative value compared to other row to decide the showing order.
        :action_index: should not be used for any serious logic.
        :result_label: tk.Label: the label where the action shows the automation result.
        :driver: orm.driver.Driver: the browser where the automation will be executed.
        :onDeleteCallback: is the function that will be executed when the row is deleted.
        """
        self.master: tk.Frame = master
        self.driver: Driver = driver
        self.action_index: int = action_index
        self.action: Action = action
        self.result_label: tk.Label = result_label
        self.onDeleteCallback: Callable[[HistoryActionRow], None] = onDeleteCallback

        # I intentionally keep the cell separately instead of grouping them under the same widget
        # so I have rooms for customization if needed to.
        # I have no concrete design after all.

        # Replay button
        def replay_in_thread() -> None:
            def replay() -> None:
                try:
                    self.retriggerHistoryAction()
                except Exception:
                    # This Exception is mainly used for when we need to replay a lot of actions.
                    # In that case, if I catch an Exception, I'll stop replay the incoming action,
                    # but in this case, I only have 1 action, so this Exception can be safely ignored.
                    # All type of data manipulation has been done by the main function with proper try catch there.
                    return
                
            threading.Thread(target=replay).start()

        self.replay_button: tk.Button = tk.Button(master=master, text="Run", anchor=tk.W, command=replay_in_thread)
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
            self.action.failed_reason = DEFAULT_FAILED_RESULT


    def retriggerHistoryAction(self) -> None:
        """retriggerHistoryAction triggered the action that was executed from the past.
        It will also update the retrigger attempt as the latest version in the history.
        It's expected for this action to take a long time to execute,
        so remember to use thread to call this function.
        """
        self.updateAction()

        # Block the execute button to prevent double clicking
        # and the remove button to avoid breaking change to the UI. 
        self.freeze()
        
        # Update the result bar to yellow hinting that it's running. 
        self.result_label.configure(background=IN_PROGRESS_BG_COLOR, text=ResultText.IN_PROGRESS)

        try:
            self.action.executeAction(driver=self.driver)
        except Exception as e:
            # Update the result label with error if there's an error
            self.result_label.configure(background=FAILED_BG_COLOR, text=ResultText.FAILED.format(e))
            raise(e)
        else:
            # Else, mark it as done.
            self.result_label.configure(background=SUCCESS_BG_COLOR, text=ResultText.SUCCESS)
        finally:
            self.unfreeze()

    
    # freeze disables the run and the remove button
    # so no severe changes can be made during the automation process. 
    def freeze(self) -> None:
        # Block the execute button to prevent double clicking.
        self.replay_button.config(state="disabled", background=IN_PROGRESS_BG_COLOR)
        # Prevent the remove button can be clicked during the automation.
        self.remove_button.config(state="disabled")

    
    # unfreeze enables the run and the remove button
    # so the row can be interactive again after the automation is done. 
    def unfreeze(self) -> None:
        # Block the execute button to prevent double clicking.
        self.replay_button.config(state="normal", background="SystemButtonFace")
        # Prevent the remove button can be clicked during the automation.
        self.remove_button.config(state="normal")


    def __onUpdateHistoryActionType(self, action_type: str) -> None:
        """onUpdateHistoryActionType updates the history action's action_type
        and re-render the data blurring."""
        if self.action.action_type != action_type:
            self.action.failed_reason = DEFAULT_FAILED_RESULT

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
        self.onDeleteCallback(self)

class ScrollableActionTable:
    def __init__(
        self,
        master: tk.Frame,
        driver: Driver,
        result_label: tk.Label,
        enable_add_row_button: bool = False) -> None:
        """
        :master: tk.Frame: The Frame where the Table will be placed.
        :driver: orm.driver.Driver: The mock browser that run the automation command from the table.
        :result_label: tk.Label: The label that shows the result of the automation command.
        """
        self.master = master
        self.driver = driver
        self.result_label: tk.Label = result_label
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

        if enable_add_row_button:
            self.add_row_button: tk.Button = tk.Button(master=self.history_table_frame, text="Add", anchor=tk.W, command=self.newEmptyRow)
            self.add_row_button.grid(row=9995, column=5, sticky=tk.E + tk.W)


    # setHeaders renders the table header.
    def setHeaders(self, headers: List[TableHeader]) -> None:
        self.headers = headers

        for i in range(len(headers)):
            header = headers[i]
            self.history_table_frame.grid_columnconfigure(index=i, weight=header.weight)
            tk.Label(master=self.history_table_frame, text=header.text, anchor=tk.W).grid(row=0, column=i, sticky=tk.N + tk.E + tk.W + tk.S)


    # addHistoryActionRow adds an action row to the list.
    # It will also render the row to the screen.
    def addHistoryActionRow(self, action: Action) -> None:
        action_row = HistoryActionRow(
            master=self.history_table_frame,
            action=action,
            action_index=len(self.rows),
            driver=self.driver,
            result_label=self.result_label,
            onDeleteCallback=self.__removeRow,
        )

        self.rows.append(action_row)


    # __updateCanvansFrameWidth makes the table's size scale with the window's resizing. 
    # https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas
    def __updateCanvansFrameWidth(self, event: tk.Event) -> None:
        canvas_width = event.width
        self.main_canvas.itemconfig(self.history_table_frame_canvas_id, width=canvas_width)


    # __onFrameConfigure updates the canvas's coverage on window resizing.
    # https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas
    def __onFrameConfigure(self, event: tk.Event) -> None:
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))


    # retriggerAll rerun ALL the actions in the table in the sequential manner.
    # retriggerAll takes a lot of time to execute so it needs to be put into a thread!
    def retriggerAll(self) -> None:
        for row in self.rows:
            try:
                row.retriggerHistoryAction()
            except Exception:
                break
            finally:
                sleep(0.5)


    # newEmptyRow add a new row to the template. 
    def newEmptyRow(self) -> None:
        action_row = HistoryActionRow(
            master=self.history_table_frame,
            action=Action(
                name="",
                action_type="",
                css="",
                failed_reason="",
                tab_index=0,
                value="",
            ),
            action_index=len(self.rows),
            driver=self.driver,
            result_label=self.result_label,
            onDeleteCallback=self.__removeRow,
        )

        self.rows.append(action_row)


    # loadData reads data from the JSON file
    # and fill up the table with rows.
    def loadData(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                actions: list[dict] = json.load(f)

            for action in actions:
                # Closure problem with python.
                # If I ever need to lock this i value, like how Go used to do "i:=i"
                # This is how python locks value.
                # 
                # for i in range(len(actions)):
                #     def run_action(i = i):
                #         try: 
                #             self.executeAction(self.history_actions[i])
                #         except Exception as e:
                #             print("Exception: {}".format(e))
                # 
                # If I do this instead:
                # 
                # for i in range(5):
                #     def run_action():
                #         index = i
                #         self.executeAction(self.history_actions[i])
                # 
                # Then. the "index" will take "i"'s reference instead of the "i" current value,
                # and the click_me function would refer to the last item.
                # Go is fine with this value locking, but not Python.
                # (Go lock by make a new reference pointing taking the same value, by reinitiating the variable using ":=")
                # 
                # By calling addHistoryActionRow with all the parameter name defined,
                # I accidentally lock the i value without knowing :3
                # In the example, is the action that is locked.
                # action_table.addHistoryActionRow(action=self.history_actions[i])
                self.addHistoryActionRow(action=Action(**action))
        except FileNotFoundError:
            pass
        except Exception as e:
            raise(e)
        pass


    # save exports the table to json.
    def save(self, filename: str) -> None:
        print("Saving...")

        # Update current rows from the UI and then
        # extract actions from all the rows.
        actions: list[Action] = []
        for row in self.rows:
            row.updateAction()
            actions.append(row.action)
        
        # Extract actions from all the rows.
        with open(filename, "w") as f:
            json.dump(actions, default=lambda o: o.encode(), indent=4, fp=f)
        
        print("Done saving...")


    # __removeRow removes the row after destroying all the widgets related to that row on the UI.
    # This will be passed around as the callback function. 
    def __removeRow(self, row: HistoryActionRow) -> None:
        self.rows.remove(row)        
