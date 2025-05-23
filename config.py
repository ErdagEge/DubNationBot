import json
import logging
import os

def load_config(file_path):
    try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from the configuration file {file_path}.")
        return None
