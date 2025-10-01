@echo off
echo Compiling Malaysia Holiday Notifier Installer...

REM Check if Inno Setup is installed in the default location
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" malaysia_holiday_notifier.iss
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    "%ProgramFiles%\Inno Setup 6\ISCC.exe" malaysia_holiday_notifier.iss
) else (
    echo Inno Setup not found in the default location.
    echo Please make sure Inno Setup is installed and try again.
    echo You can download Inno Setup from: https://jrsoftware.org/isdl.php
    goto end
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installer compilation successful!
    echo The installer has been created in the 'installer' folder.
) else (
    echo.
    echo Installer compilation failed.
    echo Please check the error messages above.
)

:end
pause
