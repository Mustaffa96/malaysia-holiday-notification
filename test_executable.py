#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Malaysia Holiday Notifier executable
This script checks if the executable was built correctly and can run
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def test_executable():
    """Test if the executable exists and can run"""
    print("Testing Malaysia Holiday Notifier executable...")
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Define path to executable
    exe_path = current_dir / "dist" / "Malaysia_Holiday_Notifier.exe"
    
    # Check if executable exists
    if not exe_path.exists():
        print(f"Error: Executable not found at {exe_path}")
        print("Please build the executable first using PyInstaller.")
        return False
    
    print(f"Found executable at {exe_path}")
    print("Starting the executable to test it...")
    
    try:
        # Start the executable
        process = subprocess.Popen([str(exe_path)])
        
        # Wait for a few seconds to see if it starts correctly
        print("Waiting for 5 seconds to check if the application starts...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("Success! The executable is running correctly.")
            
            # Ask user if they want to close the application
            response = input("Do you want to close the application now? (y/n): ")
            if response.lower() == 'y':
                process.terminate()
                print("Application terminated.")
            else:
                print("Application will continue running.")
            
            return True
        else:
            print("Error: The executable started but terminated unexpectedly.")
            return False
    
    except Exception as e:
        print(f"Error testing executable: {e}")
        return False

if __name__ == "__main__":
    test_executable()
