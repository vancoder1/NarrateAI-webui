import json
import os
import threading
import utils.logging_config as lf
from utils.constants import CONFIG_FILE_PATH

logger = lf.configure_logger(__name__)

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
        with self._lock:
            if self._initialized:
                return
            self.config_path = config_path
            self.config_data = self._load_config()
            self._initialized = True

    def _load_config(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found at {self.config_path}. Creating a default one.")
            default_config = {
                "settings": {
                    "kokoro_tts": {
                        "model_path": "models/kokoro_tts",
                        "lang_code": "a",
                        "voice": "af_heart"
                    }
                }
            }
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading config from {self.config_path}: {e}")
            raise

    def _save_config(self, data):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")
            raise

    def get_setting(self, key_path: str):
        keys = key_path.split('.')
        current_level = self.config_data
        for key in keys:
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                logger.warning(f"Setting '{key_path}' not found. Returning None.")
                return None
        return current_level

    def set_setting(self, key_path: str, value):
        keys = key_path.split('.')
        current_level = self.config_data
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                if isinstance(current_level, dict):
                    current_level[key] = value
                    logger.info(f"Setting '{key_path}' updated to '{value}'")
                else:
                    logger.error(f"Cannot set value for '{key_path}': parent is not a dictionary.")
                    return False
            else:
                if isinstance(current_level, dict) and key in current_level:
                    current_level = current_level[key]
                elif isinstance(current_level, dict):
                    current_level[key] = {}
                    current_level = current_level[key]
                else:
                    logger.error(f"Cannot traverse path '{key_path}': '{key}' is not a dictionary.")
                    return False
        self._save_config(self.config_data)
        return True