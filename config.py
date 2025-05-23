import json
import logging

def load_config(file_path: str) -> dict | None:
    """
    Loads JSON config from a file.
    Returns a dictionary or None if not found/error.
    """
    try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
    return None
