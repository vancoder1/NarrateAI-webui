import json
import os
import threading
from pathlib import Path
from loguru import logger
from utils.constants import CONFIG_FILE_PATH

class JsonHandler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config_path=CONFIG_FILE_PATH):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JsonHandler, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config_path=CONFIG_FILE_PATH):
        if self._initialized:
            return
        self.config_path = Path(config_path)
        self.config_data = self._load_config()
        self._initialized = True

    def _load_config(self):
        if not self.config_path.exists():
            logger.error(f"Config file not found at {self.config_path}.")
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        try:
            with self.config_path.open('r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.config_path}: {e}. Consider deleting or fixing the file.", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading config from {self.config_path}: {e}", exc_info=True)
            raise

    def _save_config(self, data):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}", exc_info=True)
            raise

    def get_setting(self, key_path: str, default=None):
        keys = key_path.split('.')
        current_level = self.config_data
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                logger.warning(f"Setting '{key_path}' not found. Returning default: {default}.")
                return default
        return current_level

    def set_setting(self, key_path: str, value):
        keys = key_path.split('.')
        current_level = self.config_data
        
        for i, key in enumerate(keys[:-1]):
            if not isinstance(current_level, dict):
                logger.error(f"Cannot traverse path '{key_path}': '{key}' is not a dictionary in the path.")
                return False
            current_level = current_level.setdefault(key, {}) # Ensure path exists

        if isinstance(current_level, dict):
            current_level[keys[-1]] = value
            logger.info(f"Setting '{key_path}' updated to '{value}'")
            try:
                self._save_config(self.config_data)
                return True
            except Exception:
                return False
        else:
            logger.error(f"Cannot set value for '{key_path}': final parent element is not a dictionary.")
            return False
