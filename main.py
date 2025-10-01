#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Malaysia Holiday Notifier
A PyQt5 desktop application that runs in the background and displays Windows notifications
for Malaysia holidays by scraping officeholidays.com.
"""

import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, 
                             QLabel, QListWidget, QListWidgetItem, QMainWindow,
                             QMessageBox, QPushButton, QTabWidget, QTextEdit,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

# Import custom modules
from config_manager import ConfigManager
from startup_manager import StartupManager

# Get appropriate directory for log files
def get_log_directory():
    """Get the appropriate directory for log files based on the platform.
    
    Returns:
        Path: Path object for the log directory
    """
    # Use AppData/Local on Windows
    app_name = "MalaysiaHolidayNotifier"
    
    if hasattr(sys, 'frozen'):
        # Running as compiled executable
        try:
            # First try to use user's AppData directory
            appdata_path = os.environ.get('LOCALAPPDATA')
            if appdata_path:
                log_dir = Path(appdata_path) / app_name
            else:
                # Fallback to temp directory if LOCALAPPDATA is not available
                log_dir = Path(tempfile.gettempdir()) / app_name
        except Exception:
            # Final fallback to temp directory
            log_dir = Path(tempfile.gettempdir()) / app_name
    else:
        # Running as script - use current directory
        log_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir

# Configure logging
log_file = get_log_directory() / "holiday_notifier.log"
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Log file initialized at: {log_file}")
except Exception as e:
    # If logging to file fails, set up console-only logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize log file: {e}")


class HolidayScraper(QObject):
    """Class responsible for scraping holiday data from the website."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.officeholidays.com/countries/malaysia"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.current_year = datetime.now().year
        self.next_year = self.current_year + 1

    def scrape_holidays(self) -> List[Dict[str, str]]:
        """
        Scrape holidays from the website for current and next year.

        Returns:
            List[Dict[str, str]]: List of holiday dictionaries with date, name, and day.
        """
        try:
            # Scrape current year holidays
            current_year_holidays = self._scrape_year_holidays(self.current_year)
            
            # Scrape next year holidays
            next_year_holidays = self._scrape_year_holidays(self.next_year)
            
            # Combine both years' holidays
            all_holidays = current_year_holidays + next_year_holidays
            
            logger.info(f"Successfully scraped {len(all_holidays)} holidays for {self.current_year} and {self.next_year}")
            return all_holidays

        except Exception as e:
            logger.error(f"Failed to fetch holidays: {str(e)}")
            return []
    
    def _scrape_year_holidays(self, year: int) -> List[Dict[str, str]]:
        """
        Scrape holidays for a specific year.
        
        Args:
            year (int): The year to scrape holidays for
            
        Returns:
            List[Dict[str, str]]: List of holiday dictionaries for the specified year
        """
        url = f"{self.base_url}/{year}"
        holidays = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find holiday table rows
            table = soup.find('table', class_='country-table')
            if not table:
                # Try the main URL if year-specific URL doesn't work
                if year == self.current_year:
                    return self._scrape_main_page_holidays()
                logger.warning(f"Could not find holiday table for year {year}")
                return []

            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Website format: day of week is in first column, date is in second
                    day_of_week = cols[0].get_text(strip=True)  # e.g., 'Monday'
                    date_str = cols[1].get_text(strip=True)     # e.g., 'Jan 01'
                    name = cols[2].get_text(strip=True)

                    # Parse date (format: 'MMM DD')
                    try:
                        # Add the year to the date string
                        full_date_str = f"{date_str} {year}"
                        date_obj = datetime.strptime(full_date_str, '%b %d %Y')

                        holidays.append({
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'name': name,
                            'day': day_of_week,
                            'month': date_obj.month,  # Add month for easier filtering
                            'year': year  # Add year for easier filtering
                        })
                    except ValueError:
                        logger.warning(f"Could not parse date: {date_str} for year {year}")
                        continue

            return holidays

        except Exception as e:
            logger.error(f"Failed to fetch holidays for year {year}: {str(e)}")
            return []
    
    def _scrape_main_page_holidays(self) -> List[Dict[str, str]]:
        """
        Fallback method to scrape holidays from the main page when year-specific pages fail.
        
        Returns:
            List[Dict[str, str]]: List of holiday dictionaries
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            holidays = []

            # Find holiday table rows
            table = soup.find('table', class_='country-table')
            if not table:
                logger.warning("Could not find holiday table on the website")
                return []

            rows = table.find_all('tr')[1:]  # Skip header row
            current_year = datetime.now().year

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Website format has changed: day of week is in first column, date is in second
                    day_of_week = cols[0].get_text(strip=True)  # e.g., 'Monday'
                    date_str = cols[1].get_text(strip=True)     # e.g., 'Jan 01'
                    name = cols[2].get_text(strip=True)

                    # Parse date (format: 'MMM DD')
                    try:
                        # Add the current year to the date string
                        full_date_str = f"{date_str} {current_year}"
                        date_obj = datetime.strptime(full_date_str, '%b %d %Y')

                        # If the date is in the past (more than 6 months ago), it's likely for next year
                        if (datetime.now() - date_obj).days > 180:
                            date_obj = date_obj.replace(year=current_year + 1)

                        holidays.append({
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'name': name,
                            'day': day_of_week,
                            'month': date_obj.month,  # Add month for easier filtering
                            'year': date_obj.year  # Add year for easier filtering
                        })
                    except ValueError:
                        logger.warning(f"Could not parse date: {date_str}")
                        continue

            logger.info(f"Successfully scraped {len(holidays)} holidays from main page")
            return holidays

        except Exception as e:
            logger.error(f"Failed to fetch holidays from main page: {str(e)}")
            return []


class NotificationManager(QObject):
    """Class responsible for managing notifications."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def show_notification(self, title: str, message: str) -> None:
        """
        Show a notification in the main window.

        Args:
            title (str): Notification title
            message (str): Notification message
        """
        self.main_window.add_notification(title, message)


class HolidayStorage(QObject):
    """Class responsible for storing and retrieving notified holidays."""

    def __init__(self, file_name: str = "notified_holidays.json"):
        super().__init__()
        # Get the appropriate directory for the notified holidays file
        app_dir = get_log_directory()
        self.notified_file = str(app_dir / file_name)
        self.notified_holidays = self.load_notified_holidays()

    def load_notified_holidays(self) -> List[str]:
        """
        Load previously notified holidays from file.

        Returns:
            List[str]: List of notified holiday keys
        """
        if os.path.exists(self.notified_file):
            try:
                with open(self.notified_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error decoding {self.notified_file}, starting with empty list")
                return []
        return []

    def save_notified_holidays(self) -> None:
        """Save notified holidays to file."""
        try:
            with open(self.notified_file, 'w') as f:
                json.dump(self.notified_holidays, f)
        except Exception as e:
            logger.error(f"Error saving notified holidays: {str(e)}")

    def add_holiday(self, holiday_key: str) -> None:
        """
        Add a holiday to the notified list.

        Args:
            holiday_key (str): Unique key for the holiday
        """
        if holiday_key not in self.notified_holidays:
            self.notified_holidays.append(holiday_key)
            self.save_notified_holidays()

    def is_notified(self, holiday_key: str) -> bool:
        """
        Check if a holiday has been notified.

        Args:
            holiday_key (str): Unique key for the holiday

        Returns:
            bool: True if already notified, False otherwise
        """
        return holiday_key in self.notified_holidays

    def clean_old_notifications(self, days: int = 60) -> None:
        """
        Remove notifications older than specified days.

        Args:
            days (int): Number of days to keep notifications
        """
        today = datetime.now().date()
        cutoff_date = today - timedelta(days=days)

        self.notified_holidays = [
            h for h in self.notified_holidays
            if datetime.strptime(h.split('_')[0], '%Y-%m-%d').date() > cutoff_date
        ]
        self.save_notified_holidays()


class HolidayNotifier(QMainWindow):
    """Main class for the holiday notification application."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        
        # Initialize configuration and startup managers
        self.config_manager = ConfigManager()
        self.startup_manager = StartupManager()

        # Set up the main window
        self.setWindowTitle("Malaysia Holiday Notifier")
        self.setMinimumSize(700, 600)

        # Try to load custom icon if available, prefer ICO over PNG
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_dir, "icon.ico")
        png_path = os.path.join(base_dir, "icon.png")
        
        # Prefer ICO if available, fall back to PNG
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        elif os.path.exists(png_path):
            self.setWindowIcon(QIcon(png_path))

        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create header
        header_label = QLabel("Malaysia Holiday Notifier")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)

        # Create next holiday section
        self.next_holiday_label = QLabel("Loading holiday information...")
        self.next_holiday_label.setAlignment(Qt.AlignCenter)
        next_holiday_font = QFont()
        next_holiday_font.setPointSize(12)
        self.next_holiday_label.setFont(next_holiday_font)
        main_layout.addWidget(self.next_holiday_label)

        # Create separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Create tab widget for monthly holidays, yearly holidays, and notifications
        tab_widget = QTabWidget()

        # Monthly holidays tab
        monthly_tab = QWidget()
        monthly_layout = QVBoxLayout(monthly_tab)

        monthly_label = QLabel("Holidays This Month:")
        monthly_font = QFont()
        monthly_font.setPointSize(12)
        monthly_font.setBold(True)
        monthly_label.setFont(monthly_font)
        monthly_layout.addWidget(monthly_label)

        self.monthly_holidays_list = QListWidget()
        monthly_layout.addWidget(self.monthly_holidays_list)

        tab_widget.addTab(monthly_tab, "Monthly Holidays")
        
        # Yearly holidays tab
        yearly_tab = QWidget()
        yearly_layout = QVBoxLayout(yearly_tab)
        
        yearly_header_layout = QHBoxLayout()
        
        yearly_label = QLabel("All Holidays This Year:")
        yearly_font = QFont()
        yearly_font.setPointSize(12)
        yearly_font.setBold(True)
        yearly_label.setFont(yearly_font)
        yearly_header_layout.addWidget(yearly_label)
        
        # Add year selection dropdown
        self.year_selector = QComboBox()
        current_year = datetime.now().year
        self.year_selector.addItem(str(current_year))
        self.year_selector.addItem(str(current_year + 1))
        self.year_selector.currentTextChanged.connect(self.update_yearly_holidays)
        yearly_header_layout.addWidget(self.year_selector)
        yearly_header_layout.addStretch()
        
        yearly_layout.addLayout(yearly_header_layout)
        
        # Create a tree widget for yearly holidays organized by month
        self.yearly_holidays_tree = QTreeWidget()
        self.yearly_holidays_tree.setHeaderLabels(["Date", "Holiday", "Day"])
        self.yearly_holidays_tree.setColumnWidth(0, 120)  # Date column width
        self.yearly_holidays_tree.setColumnWidth(1, 250)  # Holiday name column width
        yearly_layout.addWidget(self.yearly_holidays_tree)
        
        tab_widget.addTab(yearly_tab, "Yearly Holidays")

        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)

        notifications_label = QLabel("Recent Notifications:")
        notifications_font = QFont()
        notifications_font.setPointSize(12)
        notifications_font.setBold(True)
        notifications_label.setFont(notifications_font)
        notifications_layout.addWidget(notifications_label)

        self.notifications_text = QTextEdit()
        self.notifications_text.setReadOnly(True)
        notifications_layout.addWidget(self.notifications_text)

        tab_widget.addTab(notifications_tab, "Notifications")

        main_layout.addWidget(tab_widget)

        # Create buttons and settings
        button_layout = QHBoxLayout()

        self.check_button = QPushButton("Check Holidays Now")
        self.check_button.clicked.connect(self.check_holidays)
        button_layout.addWidget(self.check_button)
        
        # Add startup toggle checkbox
        self.startup_checkbox = QCheckBox("Run on system startup")
        self.startup_checkbox.setToolTip("When checked, the application will start automatically when you log in to Windows")
        self.startup_checkbox.setChecked(self.startup_manager.is_in_startup())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        button_layout.addWidget(self.startup_checkbox)
        
        # Add spacer to push buttons to the sides
        button_layout.addStretch()

        self.quit_button = QPushButton("Exit")
        self.quit_button.clicked.connect(self.quit_app)
        button_layout.addWidget(self.quit_button)

        main_layout.addLayout(button_layout)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Initialize components
        self.scraper = HolidayScraper()
        self.storage = HolidayStorage()
        self.notification_manager = NotificationManager(self)

        # Store holiday information
        self.next_holiday = None
        self.all_holidays = []

        # Timer to check holidays daily
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_holidays)
        self.timer.start(86400000)  # Check every 24 hours

        # Timer to update next holiday info every minute
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_next_holiday_display)
        self.update_timer.start(60000)  # Update every minute

        # Check holidays on startup (after a short delay)
        QTimer.singleShot(2000, self.check_holidays)

        # Show the window
        self.show()

        # Show welcome popup after a short delay
        QTimer.singleShot(500, self.show_welcome_popup)

    def update_next_holiday_display(self) -> None:
        """Update the next holiday display in the main window."""
        if self.next_holiday:
            holiday_date = datetime.strptime(self.next_holiday['date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            days_until = (holiday_date - today).days

            if days_until == 0:
                display_text = f"Today is a Holiday! 🎉\n{self.next_holiday['name']} ({self.next_holiday['day']})"
            elif days_until == 1:
                display_text = f"Holiday Tomorrow! 📅\n{self.next_holiday['name']} ({self.next_holiday['day']})"
            else:
                display_text = f"Next Holiday: {self.next_holiday['name']}\nIn {days_until} days ({self.next_holiday['date']}, {self.next_holiday['day']})"

            self.next_holiday_label.setText(display_text)
        else:
            self.next_holiday_label.setText("No upcoming holidays found")

    def add_notification(self, title: str, message: str) -> None:
        """Add a notification to the notifications text area."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification_text = f"[{timestamp}] {title}\n{message}\n\n"
        self.notifications_text.append(notification_text)

    def show_welcome_popup(self) -> None:
        """Show welcome popup with information about the application."""
        welcome_box = QMessageBox(self)
        welcome_box.setWindowTitle("Welcome")
        welcome_box.setIcon(QMessageBox.Information)
        welcome_box.setText("Welcome to Malaysia Holiday Notifier")

        # Information about the application features
        app_info = (
            "This application provides information about Malaysian holidays with the following features:\n\n"
            "• View holidays for the current month\n"
            "• View all holidays for the current and next year\n"
            "• Receive notifications for today's holidays\n"
            "• Automatic daily checks for upcoming holidays\n"
            "• Option to run automatically on system startup\n\n"
            "Note: This application only shows holidays for the current year and the next year. "
            "When the year changes, it will automatically update to show the new current year and the following year.\n\n"
            "NEW FEATURE: You can now set the application to run automatically when you log in to Windows. "
            "Look for the 'Run on system startup' checkbox at the bottom of the window.\n\n"
        )

        # If we have holidays for this month, include them in the welcome message
        if hasattr(self, 'all_holidays') and self.all_holidays:
            current_month = datetime.now().month
            current_year = datetime.now().year
            current_month_name = datetime.now().strftime('%B')

            this_month_holidays = []
            for holiday in self.all_holidays:
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
                if holiday_date.month == current_month and holiday_date.year == current_year:
                    this_month_holidays.append(holiday)

            # Sort by day
            this_month_holidays.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').day)

            if this_month_holidays:
                holiday_info = f"{app_info}Holidays in {current_month_name} {current_year}:\n"
                for holiday in this_month_holidays:
                    holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
                    holiday_info += f"• {holiday_date.day} {current_month_name}: {holiday['name']}\n"
                welcome_box.setInformativeText(holiday_info)
            else:
                welcome_box.setInformativeText(f"{app_info}No holidays found for {current_month_name} {current_year}.")
        else:
            welcome_box.setInformativeText(f"{app_info}Click 'Check Holidays Now' to fetch the latest holiday information.")

        welcome_box.exec_()

    def update_monthly_holidays(self) -> None:
        """Update the monthly holidays list."""
        self.monthly_holidays_list.clear()

        if not self.all_holidays:
            self.monthly_holidays_list.addItem("No holidays found. Click 'Check Holidays Now' to fetch data.")
            return

        current_month = datetime.now().month
        current_month_name = datetime.now().strftime('%B')
        current_year = datetime.now().year

        # Find holidays for the current month in the current year
        this_month_holidays = []
        for holiday in self.all_holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
            if holiday_date.month == current_month and holiday_date.year == current_year:
                this_month_holidays.append(holiday)

        # Sort by day
        this_month_holidays.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d').day)

        if this_month_holidays:
            for holiday in this_month_holidays:
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
                item_text = f"{holiday_date.day} {current_month_name}: {holiday['name']} ({holiday['day']})"

                item = QListWidgetItem(item_text)

                # Highlight today's holiday
                if holiday_date.date() == datetime.now().date():
                    item.setBackground(QColor(255, 255, 200))  # Light yellow
                    item.setForeground(QColor(0, 0, 0))  # Black text
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                # Past holidays in gray
                elif holiday_date.date() < datetime.now().date():
                    item.setForeground(QColor(128, 128, 128))  # Gray text

                self.monthly_holidays_list.addItem(item)
        else:
            self.monthly_holidays_list.addItem(f"No holidays found for {current_month_name} {current_year}.")
            
    def update_yearly_holidays(self) -> None:
        """Update the yearly holidays tree with holidays for the selected year."""
        self.yearly_holidays_tree.clear()
        
        if not self.all_holidays:
            return
            
        # Get selected year
        selected_year = int(self.year_selector.currentText())
        
        # Dictionary to store month nodes
        month_nodes = {}
        
        # Month names
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        # Create month nodes
        for month_num, month_name in enumerate(month_names, 1):
            month_node = QTreeWidgetItem(self.yearly_holidays_tree)
            month_node.setText(0, month_name)
            month_node.setExpanded(True)  # Expand all months by default
            month_nodes[month_num] = month_node
        
        # Filter holidays for the selected year
        year_holidays = [h for h in self.all_holidays if datetime.strptime(h['date'], '%Y-%m-%d').year == selected_year]
        
        today = datetime.now().date()
        
        # Add holidays to their respective months
        for holiday in year_holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
            month_num = holiday_date.month
            
            if month_num in month_nodes:
                holiday_item = QTreeWidgetItem(month_nodes[month_num])
                
                # Format as "DD Month: Holiday Name (Day)"
                date_str = f"{holiday_date.day:02d} {month_names[month_num-1]}"
                
                holiday_item.setText(0, date_str)
                holiday_item.setText(1, holiday['name'])
                holiday_item.setText(2, holiday['day'])
                
                # Highlight today's holiday
                if holiday_date.date() == today:
                    for col in range(3):  # Apply to all columns
                        holiday_item.setBackground(col, QColor(255, 255, 200))  # Light yellow
                        font = holiday_item.font(col)
                        font.setBold(True)
                        holiday_item.setFont(col, font)
                # Past holidays in gray
                elif holiday_date.date() < today:
                    for col in range(3):  # Apply to all columns
                        holiday_item.setForeground(col, QColor(128, 128, 128))  # Gray text
        
        # Remove empty months
        for month_num, month_node in list(month_nodes.items()):
            if month_node.childCount() == 0:
                index = self.yearly_holidays_tree.indexOfTopLevelItem(month_node)
                self.yearly_holidays_tree.takeTopLevelItem(index)

    def check_holidays(self) -> None:
        """Check for holidays and show notifications."""
        logger.info("Checking for holidays...")
        self.check_button.setEnabled(False)
        self.check_button.setText("Checking...")

        holidays = self.scraper.scrape_holidays()
        if not holidays:
            logger.warning("No holidays found or error occurred")
            self.add_notification("Warning", "No holidays found or error occurred")
            self.check_button.setEnabled(True)
            self.check_button.setText("Check Holidays Now")
            return

        # Store all holidays
        self.all_holidays = holidays

        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        week_ahead = today + timedelta(days=7)

        # Find next upcoming holiday
        upcoming_holidays = []
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            if holiday_date >= today:
                upcoming_holidays.append(holiday)

        # Sort upcoming holidays by date
        upcoming_holidays.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

        # Set next holiday if available
        if upcoming_holidays:
            self.next_holiday = upcoming_holidays[0]
            self.update_next_holiday_display()
        else:
            self.next_holiday = None
            self.next_holiday_label.setText("No upcoming holidays found")

        # Update monthly and yearly holidays displays
        self.update_monthly_holidays()
        self.update_yearly_holidays()

        for holiday in holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            holiday_key = f"{holiday['date']}_{holiday['name']}"

            # Skip if already notified
            if self.storage.is_notified(holiday_key):
                continue

            # Check if holiday is today
            if holiday_date == today:
                self.notification_manager.show_notification(
                    "Holiday Today! 🎉",
                    f"{holiday['name']}\n{holiday['day']}"
                )
                self.storage.add_holiday(holiday_key)

            # Check if holiday is tomorrow
            elif holiday_date == tomorrow:
                self.notification_manager.show_notification(
                    "Holiday Tomorrow! 📅",
                    f"{holiday['name']}\n{holiday['day']}"
                )
                self.storage.add_holiday(holiday_key)

            # Check if holiday is within a week
            elif today < holiday_date <= week_ahead:
                days_until = (holiday_date - today).days
                self.notification_manager.show_notification(
                    f"Upcoming Holiday in {days_until} days",
                    f"{holiday['name']}\n{holiday['date']} ({holiday['day']})"
                )
                self.storage.add_holiday(holiday_key)

        # Clean up old notified holidays
        self.storage.clean_old_notifications()

        self.check_button.setEnabled(True)
        self.check_button.setText("Check Holidays Now")

    def toggle_startup(self, state) -> None:
        """Toggle application startup status.
        
        Args:
            state: Checkbox state (Qt.Checked or Qt.Unchecked)
        """
        if state == Qt.Checked:
            success = self.startup_manager.add_to_startup()
            if success:
                logger.info("Added application to startup")
                self.config_manager.set_setting("run_on_startup", True)
                self.add_notification("Startup Setting", "Application will now run on system startup")
            else:
                logger.error("Failed to add application to startup")
                self.add_notification("Startup Setting Error", "Failed to add application to startup")
                # Reset checkbox without triggering the event
                self.startup_checkbox.blockSignals(True)
                self.startup_checkbox.setChecked(False)
                self.startup_checkbox.blockSignals(False)
        else:
            success = self.startup_manager.remove_from_startup()
            if success:
                logger.info("Removed application from startup")
                self.config_manager.set_setting("run_on_startup", False)
                self.add_notification("Startup Setting", "Application will no longer run on system startup")
            else:
                logger.error("Failed to remove application from startup")
                self.add_notification("Startup Setting Error", "Failed to remove application from startup")
                # Reset checkbox without triggering the event
                self.startup_checkbox.blockSignals(True)
                self.startup_checkbox.setChecked(True)
                self.startup_checkbox.blockSignals(False)

    def quit_app(self) -> None:
        """Quit the application."""
        logger.info("Application shutting down")
        self.app.quit()

    def run(self) -> None:
        """Run the application."""
        logger.info("Starting Malaysia Holiday Notifier")
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    notifier = HolidayNotifier()
    notifier.run()
