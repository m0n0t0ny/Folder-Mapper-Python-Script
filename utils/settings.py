import json
import os
import logging

SETTINGS_FILE = "folder_mapper_settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                logging.info("Settings loaded successfully.")
                return settings
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return {}
    logging.warning(f"Settings file {SETTINGS_FILE} not found.")
    return {}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
            logging.info("Settings saved successfully.")
    except Exception as e:
        logging.error(f"Error saving settings: {e}")
