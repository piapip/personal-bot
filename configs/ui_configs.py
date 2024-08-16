GUI_SIZE = "700x500"

# List of key to map from key --> tk object.
################################################
# TAB
ACTION_TAB_KEY = "Action tab key"
HISTORY_TAB_KEY = "History tab key"
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
RESULT_KEY = "Result key"
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
