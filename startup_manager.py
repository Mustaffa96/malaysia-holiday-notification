#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Startup Manager for Malaysia Holiday Notifier
Handles adding/removing the application from Windows startup.
"""

import os
import sys
import logging
import winreg
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


class StartupManager:
    """Class responsible for managing application startup settings."""

    def __init__(self, app_name: str = "MalaysiaHolidayNotifier"):
        """
        Initialize the startup manager.

        Args:
            app_name (str): Name of the application for registry key
        """
        self.app_name = app_name
        self.reg_key = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def is_in_startup(self) -> bool:
        """
        Check if the application is set to run on startup.

        Returns:
            bool: True if in startup, False otherwise
        """
        try:
            # Open the registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_key) as key:
                # Try to get the value, if it exists
                winreg.QueryValueEx(key, self.app_name)
                return True
        except FileNotFoundError:
            # Registry key doesn't exist
            return False
        except WindowsError:
            # Registry value doesn't exist
            return False

    def add_to_startup(self) -> bool:
        """
        Add the application to Windows startup.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the full path to the executable or script
            if getattr(sys, 'frozen', False):
                # If the application is frozen (PyInstaller)
                app_path = f'"{sys.executable}"'
            else:
                # If running as a script, use the batch file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                batch_path = os.path.join(script_dir, "start_notifier.bat")
                app_path = f'"{batch_path}"'

            # Open the registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_key, 0, 
                               winreg.KEY_WRITE) as key:
                # Set the value
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, app_path)
            
            logger.info(f"Added {self.app_name} to startup with path: {app_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add to startup: {str(e)}")
            return False

    def remove_from_startup(self) -> bool:
        """
        Remove the application from Windows startup.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the application is in startup
            if not self.is_in_startup():
                logger.info(f"{self.app_name} is not in startup")
                return True

            # Open the registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_key, 0, 
                               winreg.KEY_WRITE) as key:
                # Delete the value
                winreg.DeleteValue(key, self.app_name)
            
            logger.info(f"Removed {self.app_name} from startup")
            return True
        except Exception as e:
            logger.error(f"Failed to remove from startup: {str(e)}")
            return False

    def toggle_startup(self) -> bool:
        """
        Toggle the startup status.

        Returns:
            bool: New startup status (True if added, False if removed)
        """
        if self.is_in_startup():
            self.remove_from_startup()
            return False
        else:
            self.add_to_startup()
            return True
