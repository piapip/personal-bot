from tkinter import ttk, simpledialog
import tkinter as tk
import threading
from pathlib import Path
import os
import re
import time

from configs.ui_configs import (
    ResultText,
)
from helpers.ui import StyledEntry
from orm.driver import Driver
from orm.scrollable_table import (
    ScrollableActionTable,
)

class Template:
    def __init__(self, master: ttk.Notebook, driver: Driver, name: str) -> None:
        self.master: ttk.Notebook = master
        self.name: str = name
        self.driver: Driver = driver
        # continue_next_step hints us if the template is running or not.
        # True means that the Template is running.
        # False means that the Template is either terminated or not running.
        self.continue_next_step: bool = False
        
        self.main_ui: tk.Frame = tk.Frame(master=master)
        # The default content of the template tab.
        # The layout would be:
        #   1. Header: The result label and progress bar.
        #      The template can be looped over and over for a very long time,
        #      so I need to keep myself up to date about the processing of each template,
        #      therefore, it would be to the top, and each template will have its own result_label.
        #   2. Middle part containing all the actions.
        #      2.1. Start with the header.
        #      2.2. Normally, template would start on an empty slate.
        #           Later, when the user stores templates,
        #           the content will be rendered by importing file via the action_table. 

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

        # Frame for the the "Repeat count" entry and the Progress bar.
        progress_bar_frame: tk.Frame = tk.Frame(master=self.top_frame)
        progress_bar_frame.pack(fill="x", padx=10, pady=10)
        progress_bar_frame.columnconfigure(index=0, weight=1, uniform="tag")
        progress_bar_frame.columnconfigure(index=1, weight=1, uniform="tag")
        progress_bar_frame.columnconfigure(index=2, weight=10, uniform="tag")

        self.repeat_count_label_variable: tk.StringVar = tk.StringVar()
        self.repeat_count_label_variable.set("Repeat: 0/")
        tk.Label(master=progress_bar_frame, textvariable=self.repeat_count_label_variable, width=12, anchor=tk.E, ).grid(row=0, column=0, sticky=tk.W + tk.E)
        self.repeat_count_entry: ttk.Entry = StyledEntry(master=progress_bar_frame)
        self.repeat_count_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.repeat_count_entry.insert(index=0, string="1")

        self.progress_percent = tk.IntVar()
        self.progress_bar: ttk.Progressbar = ttk.Progressbar(master=progress_bar_frame, orient=tk.HORIZONTAL, variable=self.progress_percent)
        self.progress_bar.grid(row=0, column=2, sticky=tk.W + tk.E)

        # [2]
        # Now actually filling in the table of the middle_frame.
        self.action_table: ScrollableActionTable = ScrollableActionTable(
            master=self.middle_frame,
            driver=self.driver,
            result_label=self.result_label,
            enable_add_row_button=True)


    # retriggerAllRows rerun ALL the actions in the table in the sequential manner.
    # retriggerAllRows takes a lot of time to execute so it needs to be put into a thread!
    def retriggerAllRows(self) -> None:
        # Reset the repeat count on the UI.
        # And mark that this template is running.
        self.repeat_count_label_variable.set("Repeat: 0/")
        self.continue_next_step = True
        self.repeat_count_entry.config(state="readonly")
        self.action_table.add_row_button.config(state="disabled")

        repeat = int(self.repeat_count_entry.get())

        total_task_count = repeat * len(self.action_table.rows)
        task_done_count = 0
        for i in range(repeat):
            if not self.continue_next_step:
                self.result_label.configure(text="Paused")
                break

            for row in self.action_table.rows:
                try:
                    row.retriggerHistoryAction()
                except Exception:
                    break
                finally:
                    task_done_count += 1
                    self.progress_percent.set(int(100*task_done_count/total_task_count))
                    # This can be turned off by calling urgentPause.
                    if not self.continue_next_step:
                        break
                    else:
                        time.sleep(0.5)
            # Update the retry attempt count on the UI after a cycle is done. 
            self.repeat_count_label_variable.set("Repeat: {}/".format(i+1))
                    

        # Mark that this template is done running.
        self.continue_next_step = False
        self.repeat_count_entry.config(state="normal")
        self.action_table.add_row_button.config(state="normal")


    # run executes all the actions of the template one by one.
    def run(self) -> None:
        execution_thread = threading.Thread(target=self.retriggerAllRows)
        execution_thread.start()


    # urgentPause stops the template's execution after its current step is finished.
    def urgentPause(self) -> None:
        # self.result_label.
        if self.continue_next_step:
            self.continue_next_step = False
            self.result_label.configure(text=ResultText.PAUSE_NOTIFICATION)


class TabTemplates:
    def __init__(self, master: ttk.Notebook, driver: Driver) -> None:
        self.master: ttk.Notebook = master
        self.driver: Driver = driver
        
        # Make the template folder if not exists.
        self.history_folder = "./templates"
        Path(self.history_folder).mkdir(parents=True, exist_ok=True)

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
        self.run_button = tk.Button(master=self.top_frame, text="Run", width="6", command=self.__runTemplate)
        self.run_button.pack(side=tk.LEFT)

        self.urgent_pause_button = tk.Button(master=self.top_frame, text="Pause", width="6", command=self.__urgentPauseTemplate)
        self.urgent_pause_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(master=self.top_frame, text="Save", width="6", command=self.__saveCurrentTemplate)
        self.save_button.pack(side=tk.LEFT)

        self.save_all_button = tk.Button(master=self.top_frame, text="Save all", width="6", command=self.__saveAll)
        self.save_all_button.pack(side=tk.LEFT)

        # TODO [11]: Add a hotkey for this?
        self.rename_button = tk.Button(master=self.top_frame, text="Rename", width="6", command=self.__onRenameTab)
        self.rename_button.pack(side=tk.LEFT)

        self.import_button = tk.Button(master=self.top_frame, text="Import", width="6")
        self.import_button.pack(side=tk.RIGHT)

        self.export_button = tk.Button(master=self.top_frame, text="Export", width="6")
        self.export_button.pack(side=tk.RIGHT)

        # [2] Setup the template zone for the middle_frame.
        self.template_tabs_control: ttk.Notebook = ttk.Notebook(master=self.middle_frame, padding=(0, 4, 0, 0))
        self.template_tabs_control.pack(expand=1, fill="both")

        # For the middle_frame that includes templates, initiate with
        #   [2.1.] an empty template
        #   [2.2.] a "add new template" button,
        # like how we do in the browser.
        
        # [2.1.]
        self.load()

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
            # Change the name on the UI
            self.template_tabs_control.tab(self.template_tabs_control.select(), text=response)
            # Then change the name of the file that stored the data.
            current_tab_index: int = self.template_tabs_control.index(self.template_tabs_control.select())
            current_template: Template = self.templates[current_tab_index]
            
            current_template_file_name = self.history_folder + "/" + str(current_tab_index) + "_" + current_template.name + ".json"
            template_json_file = Path(current_template_file_name)
            if template_json_file.is_file():
                new_template_file_name = self.history_folder + "/" + str(current_tab_index) + "_" + response + ".json"
                os.rename(current_template_file_name, new_template_file_name)
            
            current_template.name = response

    
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
            template_name = "Template {}".format(index + 1)
            new_template = Template(master=self.template_tabs_control, driver=self.driver, name=template_name)
            self.template_tabs_control.insert(index, child=new_template.main_ui, text=new_template.name)
            self.template_tabs_control.select(index)
            self.templates.append(new_template)

    
    # __runTemplate run all the actions of the selected template.
    def __runTemplate(self) -> None:
        current_tab_index: int = self.template_tabs_control.index(self.template_tabs_control.select())
        current_template: Template = self.templates[current_tab_index]
        current_template.run()


    # __urgentPauseTemplate stops the template from continuing after its current step execution.
    def __urgentPauseTemplate(self) -> None:
        current_tab_index: int = self.template_tabs_control.index(self.template_tabs_control.select())
        current_template: Template = self.templates[current_tab_index]
        current_template.urgentPause()


    # __saveCurrentTemplate exports the current selected template to json.
    def __saveCurrentTemplate(self) -> None:
        # TODO [19]: Duplicated template's name won't crash the saving process.
        # It can be done by exporting this into dict (map ID -> actual Template)
        # ID will be the diffentiator now.
        # Though, that'll make the import feature kinda annoying, because I'll need to merge 2 json files.
        current_tab_index: int = self.template_tabs_control.index(self.template_tabs_control.select())
        current_template: Template = self.templates[current_tab_index]
        
        filename = self.history_folder + "/" + str(current_tab_index) + "_" + current_template.name + ".json"
        current_template.action_table.save(filename=filename)


    # __saveAll traverse through all the templates, updates, and saves all of them. 
    def __saveAll(self) -> None:
        for i in range(len(self.templates)):
            template = self.templates[i]
            filename = self.history_folder + "/" + str(i) + "_" + template.name + ".json"
            template.action_table.save(filename=filename)


    # load pulls all the templates from the previous attempts and put them to the screen.
    def load(self) -> None:
        filename_regex = "[0-9+]_(.*).json"
        
        for file in os.listdir(self.history_folder):
            file_name = os.fsdecode(file)
            template_name = re.search(pattern=filename_regex, string=file_name).group(1)
            
            template = Template(
                master=self.template_tabs_control,
                driver=self.driver,
                name=template_name)
            template.action_table.loadData(self.history_folder + "/" + file_name)
            self.template_tabs_control.add(child=template.main_ui, text=template.name)
            self.templates.append(template)

