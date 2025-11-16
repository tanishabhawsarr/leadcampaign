# # state_manager.py
# import json
# import os

# STATE_FILE = "last_state.json"

# def load_last_processed():
#     if not os.path.exists(STATE_FILE):
#         return None
#     try:
#         with open(STATE_FILE, "r") as f:
#             data = json.load(f)
#             return data.get("last_processed")
#     except:
#         return None


# def save_last_processed(timestamp):
#     with open(STATE_FILE, "w") as f:
#         json.dump({"last_processed": timestamp}, f)



# state_manager.py

import json
import os

STATE_FILE = "last_state.json"


def load_last_processed():
    """Load last processed datetime string from local file"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_processed")
    except:
        return None


def save_last_processed(timestamp_string):
    """Save the latest processed datetime string to local file"""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_processed": timestamp_string}, f)
