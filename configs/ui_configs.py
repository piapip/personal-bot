GUI_SIZE = "750x350"

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
