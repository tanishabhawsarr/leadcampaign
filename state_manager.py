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

# import json
# import os

# STATE_FILE = "last_state.json"


# def load_last_processed():
#     """Load last processed datetime string from local file"""
#     if not os.path.exists(STATE_FILE):
#         return None
#     try:
#         with open(STATE_FILE, "r") as f:
#             data = json.load(f)
#             return data.get("last_processed")
#     except:
#         return None


# def save_last_processed(timestamp_string):
#     """Save the latest processed datetime string to local file"""
#     with open(STATE_FILE, "w") as f:
#         json.dump({"last_processed": timestamp_string}, f)


# state_manager.py
import json
import os

# Local pe: current folder
# Azure App Service pe: env var STATE_DIR = /home/site/wwwroot (App Settings me set kar dena)
BASE_DIR = os.getenv("STATE_DIR") or os.getcwd()
STATE_FILE = os.path.join(BASE_DIR, "last_state.json")


def load_last_processed():
    """Load last processed datetime string from local/azure file"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_processed")
    except:
        return None


def save_last_processed(timestamp_string):
    """Save the latest processed datetime string to local/azure file"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_processed": timestamp_string}, f)
