# Import necessary modules for file handling and JSON serialization
import json
import os

# Define the JSON file path used to store user chat or session history
FILE = "healthbackend/storage/history.json"


# ------------------------------------------------------------
# Load function
# ------------------------------------------------------------
# Purpose: Read and return the stored data from the history file.
# Returns an empty dictionary if the file doesn't exist.
def load():
    if not os.path.exists(FILE):
        # If no history file exists, return an empty dictionary
        return {}
    # Open the existing file and load its JSON content
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# Save function
# ------------------------------------------------------------
# Purpose: Write the given data back into the JSON file, creating directories if needed.
def save(data):
    # Ensure the directory structure exists before writing the file
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    # Write the data as formatted JSON with indentation for readability
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------------------------------------------------
# Save user history entry
# ------------------------------------------------------------
# Purpose: Append a new history entry for a specific user.
# If the user does not exist, initialize their entry as an empty list.
def save_history(user_id, entry):
    # Load the existing history structure
    data = load()
    # Create a list for the user if not present and append the new entry
    data.setdefault(user_id, []).append(entry)
    # Save updated data back to storage
    save(data)


# ------------------------------------------------------------
# Retrieve user history
# ------------------------------------------------------------
# Purpose: Fetch the conversation or history list for a given user.
# Returns an empty list if the user has no recorded history.
def get_history(user_id):
    return load().get(user_id, [])
