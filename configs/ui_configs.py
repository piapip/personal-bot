GUI_SIZE = "1250x500"

# List of key to map from key --> tk object.
################################################
# TAB
ACTION_TAB_KEY = "Action tab key"
HISTORY_TAB_KEY = "History tab key"     # HISTORY_TAB_KEY is for the Actions History tab.
HISTORY_TABLE_KEY = "History table key" # HISTORY_TABLE_KEY is for the table in the HISTORY_TAB.
################################################
# INPUT LABEL
NAME_ENTRY_KEY = "Name entry key"
CSS_SELECTOR_ENTRY_KEY = "CSS Selector entry key"
VALUE_ENTRY_KEY = "Value entry key"
TAB_INDEX_KEY = "Tab position entry key"
################################################
# INPUT ACTION
ACTION_OPTION_BOX_KEY = "Action option box "
from enum import StrEnum
################################################
# OUTPUT AUTOMATION
SINGLE_ACTION_RESULT_KEY = "Single action result key"
HISTORY_ACTION_RESULT_KEY = "History action result key"
# FOOTER_GRID_ROW is the grid value of the item that is at the footer of the UI.
# 
# Because it's impossible to always put stuff at the bottom using grid.
# But grid is such a handy tool for making a table.
# There's soft limit set by tkinter where there can only be 9998 rows so that will be this thing's soft limit as well.
# 
# This value can also be changed to limit actions in history later.
# That way will assure that we'll never exceed the self-defined cap of 9995 (-1 for the header, -1 for the result) actions per page.
FOOTER_GRID_ROW = 9998
class ResultText(StrEnum):
    IN_PROGRESS = "Please wait. Executing..."
    SUCCESS = "Success"
    FAILED = "Step failed because of: {}"
################################################
# HISTORY TABLE
HISTORY_TABLE_KEY = "History table"
################################################
# HISTORY TABLE
EXECUTE_BUTTON_KEY = "Execute button key"
################################################
