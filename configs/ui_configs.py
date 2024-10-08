GUI_SIZE = "750x450"

# List of key to map from key --> tk object.
################################################
# TABS
ACTION_TAB_KEY = "Action tab key"
HISTORY_TAB_KEY = "History tab key"     # HISTORY_TAB_KEY is for the History tab.
################################################
from enum import StrEnum
################################################
# OUTPUT AUTOMATION
class ResultText(StrEnum):
    IN_PROGRESS = "Please wait. Executing..."
    SUCCESS = "Success"
    FAILED = "{}"
    PAUSE_NOTIFICATION = "Pause after this action is done..."
################################################
# HISTORY TABLE
# the default error message for the action that is not executed yet. 
DEFAULT_FAILED_RESULT = "not execute yet!"
################################################
# PROGRESS BACKGROUND COLOR
IN_PROGRESS_BG_COLOR = "#f3e96c"
FAILED_BG_COLOR = "#f13c1c"
SUCCESS_BG_COLOR = "#3af40d"
################################################
