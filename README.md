# Malaysia Holiday Notification

<img width="700" height="645" alt="image" src="https://github.com/user-attachments/assets/ab7f0203-67b6-4eab-a674-fc1a616f66fc" />


A Windows desktop application that displays notifications for Malaysian holidays. The application scrapes holiday information from [officeholidays.com](https://www.officeholidays.com/countries/malaysia) and provides timely notifications for upcoming holidays.

## Features

- 🌐 Automatically scrapes Malaysia holidays from officeholidays.com
- 📅 Shows notifications for:
  - Holidays happening today
  - Holidays tomorrow
  - Upcoming holidays within the next 7 days
- 💬 Displays next upcoming holiday information prominently in the main window
- 📊 Tabbed interface with:
  - Monthly view showing holidays for the current month
  - Yearly view showing all holidays organized by month
  - Notifications tab showing recent holiday alerts
- 🗓️ Year selector to view holidays for current or next year (automatically updates when the year changes)
- ⏰ Checks holidays automatically every 24 hours
- 🔄 Prevents duplicate notifications
- 🚀 Option to run automatically on system startup
- 🔽 Simple user interface with "Check Holidays Now" and "Exit" buttons

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Mustaffa96/malaysia-holiday-notification.git
   cd malaysia-holiday-notification
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

You can run the application in several ways:

1. Using Python directly:
   ```bash
   python main.py
   ```

2. Using the batch file (Windows):
   ```bash
   start_notifier.bat
   ```

The application will start and display a window showing upcoming holiday information. It will automatically check for holidays on startup and then every 24 hours.

### Application Interface

- **Main Window**: Displays the next upcoming holiday with countdown
- **Monthly Holidays Tab**: Shows holidays for the current month
  - Today's holidays are highlighted in yellow
  - Past holidays are shown in gray
- **Yearly Holidays Tab**: Shows all holidays for the selected year organized by month
  - Expandable tree view with months as parent nodes
  - Ability to switch between current and next year
  - Today's holidays are highlighted in yellow
  - Past holidays are shown in gray
- **Notifications Tab**: Shows recent holiday notifications
- **Check Holidays Now**: Button to manually check for holidays
- **Run on system startup**: Checkbox to toggle automatic startup when you log in to Windows
- **Exit**: Button to close the application

## Auto-start with Windows

The application includes a built-in feature to run automatically when you log in to Windows:

1. Simply check the "Run on system startup" checkbox at the bottom of the main window
2. The application will now start automatically when you log in to Windows
3. You can disable this feature at any time by unchecking the checkbox

Alternatively, you can manually set up auto-start:

1. Press `Win + R`, type `shell:startup`, and press Enter
2. Create a shortcut to your Python script or executable in that folder

## How It Works

1. The application runs as a regular window application
2. It scrapes holiday data from officeholidays.com for both the current and next year (when the current year ends, it automatically updates to show the new current year and the following year)
3. The main window displays information about the next upcoming holiday
4. The tabbed interface provides three views:
   - Monthly tab: Shows holidays for the current month
   - Yearly tab: Shows all holidays for the selected year organized by month
   - Notifications tab: Shows recent holiday alerts
5. When a holiday is detected (today, tomorrow, or within a week), it shows a notification in the application
6. Previously notified holidays are stored in a JSON file to avoid duplicate notifications
7. Old notifications (older than 60 days) are automatically cleaned up
8. The holiday information updates every minute to show accurate countdown to the next holiday
9. Users can switch between current and next year in the Yearly Holidays tab
10. The application can be configured to run automatically when Windows starts up
11. Startup preferences are stored in the app_config.json file
12. All application data (logs, configuration, and notified holidays) is stored in the user's AppData directory to avoid permission issues

## Project Structure

### Core Application Files
- `main.py`: Main application code
- `config_manager.py`: Module for managing application configuration
- `startup_manager.py`: Module for managing Windows startup integration
- `check_website.py`: Module for scraping holiday data from the website
- `requirements.txt`: Required Python dependencies
- `create_icon.py`: Script to generate the application icon
- `start_notifier.bat`: Batch file for easy startup on Windows
- `notified_holidays.json`: Storage for previously notified holidays (created automatically in user's AppData directory)
- `app_config.json`: Application configuration file (created automatically in user's AppData directory)
- `holiday_notifier.log`: Application log file (created automatically in user's AppData directory)
- `icon.png`: Application icon in PNG format (created by running create_icon.py)
- `icon.ico`: Application icon in ICO format for Windows and installers (created by running create_icon.py)

### Build and Distribution Files
- `malaysia_holiday_notifier.spec`: PyInstaller spec file for building the executable
- `build_exe.py`: Script to build the executable using PyInstaller
- `build_executable.bat`: Batch file to run the build script
- `build_with_spec.bat`: Batch file to build using the spec file directly
- `test_executable.py`: Script to test if the executable works correctly
- `test_executable.bat`: Batch file to run the test script
- `create_installer.py`: Script to create a Windows installer using NSIS
- `create_installer.bat`: Batch file to run the installer creation script
- `QUICK_START.md`: Quick start guide for building and distributing the application

### Development and Quality Assurance
- `.flake8`: Configuration for flake8 linter
- `.pylintrc`: Configuration for pylint linter
- `fix_style.py`: Script to automatically fix common style issues

## Development

### Code Quality and Linting

This project uses several tools to maintain code quality:

1. **Flake8**: For style guide enforcement and error detection
   ```bash
   flake8 main.py check_website.py create_icon.py
   ```

2. **Pylint**: For more comprehensive code analysis
   ```bash
   pylint main.py check_website.py create_icon.py
   ```

3. **Automatic Style Fixing**:
   ```bash
   python fix_style.py
   ```
   This script will:
   - Remove trailing whitespace
   - Fix blank lines between functions and classes
   - Sort imports (if isort is installed)
   - Remove unused imports (if autoflake is installed)

4. **Install Development Dependencies**:
   ```bash
   pip install flake8 pylint isort autoflake
   ```
   Or simply use the requirements.txt which includes these tools.

## Building Executable

You can build a standalone executable file that doesn't require Python to be installed. For quick instructions, see the [QUICK_START.md](QUICK_START.md) guide.

### Using PyInstaller Directly

1. Make sure you have PyInstaller installed:
   ```bash
   pip install pyinstaller
   ```

2. Build using the spec file:
   ```bash
   pyinstaller malaysia_holiday_notifier.spec
   ```

3. The executable will be created in the `dist` folder as `Malaysia_Holiday_Notifier.exe`


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
