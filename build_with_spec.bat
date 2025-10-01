@echo off
echo Building Malaysia Holiday Notifier executable using spec file...
pyinstaller malaysia_holiday_notifier.spec
echo.
echo If the build was successful, the executable is available in the dist folder.
pause
