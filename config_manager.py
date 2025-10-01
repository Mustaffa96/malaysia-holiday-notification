#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager for Malaysia Holiday Notifier
Handles reading and writing application configuration settings.
"""

import json
import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)


def get_app_data_directory():
    """Get the appropriate directory for application data based on the platform.
    
    Returns:
        Path: Path object for the app data directory
    """
    # Use AppData/Local on Windows
    app_name = "MalaysiaHolidayNotifier"
    
    if hasattr(sys, 'frozen'):
        # Running as compiled executable
        try:
            # First try to use user's AppData directory
            appdata_path = os.environ.get('LOCALAPPDATA')
            if appdata_path:
                app_dir = Path(appdata_path) / app_name
            else:
                # Fallback to temp directory if LOCALAPPDATA is not available
                app_dir = Path(tempfile.gettempdir()) / app_name
        except Exception:
            # Final fallback to temp directory
            app_dir = Path(tempfile.gettempdir()) / app_name
    else:
        # Running as script - use current directory
        app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure directory exists
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


class ConfigManager:
    """Class responsible for managing application configuration."""

    def __init__(self, config_file: str = "app_config.json"):
        """
        Initialize the configuration manager.

        Args:
            config_file (str): Name of the configuration file
        """
        # Get the appropriate directory for the config file
        app_dir = get_app_data_directory()
        self.config_file = str(app_dir / config_file)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        default_config = {
            "run_on_startup": False,
            "check_interval_hours": 24,
            "notification_days_ahead": 7
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Ensure all default keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except json.JSONDecodeError:
                logger.error(f"Error decoding {self.config_file}, using default configuration")
                return default_config
        return default_config

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting.

        Args:
            key (str): Setting key
            default (Any, optional): Default value if key doesn't exist

        Returns:
            Any: Setting value
        """
        return self.config.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a configuration setting.

        Args:
            key (str): Setting key
            value (Any): Setting value
        """
        self.config[key] = value
        self.save_config()
