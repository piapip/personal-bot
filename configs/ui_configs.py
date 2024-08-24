GUI_SIZE = "750x450"

# List of key to map from key --> tk object.
################################################
# TABS
ACTION_TAB_KEY = "Action tab key"
HISTORY_TAB_KEY = "History tab key"     # HISTORY_TAB_KEY is for the History tab.
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
    FAILED = "{}"
################################################
# HISTORY TABLE
EXECUTE_BUTTON_KEY = "Execute button key"
################################################
# PROGRESS BACKGROUND COLOR
IN_PROGRESS_BG_COLOR = "#f3e96c"
FAILED_BG_COLOR = "#f13c1c"
SUCCESS_BG_COLOR = "#3af40d"
################################################
