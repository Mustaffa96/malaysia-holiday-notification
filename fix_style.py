#!/usr/bin/env python
"""
Script to automatically fix common style issues in Python files:
- Remove trailing whitespace
- Ensure proper blank lines between functions and classes
- Fix import order
- Remove unused imports (requires autoflake)
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from all lines in a file."""
    print(f"Fixing trailing whitespace in {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove trailing whitespace from each line
    fixed_content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)

def ensure_blank_lines(file_path):
    """Ensure proper blank lines between functions and classes."""
    print(f"Fixing blank lines in {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    result = []
    in_class_or_func = False
    blank_lines_count = 0
    
    for i, line in enumerate(lines):
        # Check for class or function definition
        if re.match(r'^(class|def)\s+', line) and i > 0:
            # If we're starting a new class or top-level function, ensure 2 blank lines before
            if not in_class_or_func or re.match(r'^class\s+', line) or re.match(r'^def\s+', lines[i-blank_lines_count-1]):
                # Ensure exactly 2 blank lines before class/function definitions
                while blank_lines_count < 2:
                    result.append('\n')
                    blank_lines_count += 1
            in_class_or_func = True
        
        # Count consecutive blank lines
        if line.strip() == '':
            blank_lines_count += 1
        else:
            blank_lines_count = 0
        
        result.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(result)

def main():
    """Main function to fix style issues in Python files."""
    # Get all Python files in the project
    python_files = list(Path('.').glob('**/*.py'))
    
    for file_path in python_files:
        # Skip this script itself
        if file_path.name == os.path.basename(__file__):
            continue
            
        str_path = str(file_path)
        fix_trailing_whitespace(str_path)
        ensure_blank_lines(str_path)
        
        # Try to run autoflake if available (removes unused imports)
        try:
            subprocess.run(['autoflake', '--in-place', '--remove-all-unused-imports', str_path], 
                          check=True, capture_output=True)
            print(f"Removed unused imports in {str_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Note: autoflake not available. Install with 'pip install autoflake' to remove unused imports")
        
        # Try to run isort if available (sorts imports)
        try:
            subprocess.run(['isort', str_path], check=True, capture_output=True)
            print(f"Sorted imports in {str_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Note: isort not available. Install with 'pip install isort' to sort imports")

if __name__ == "__main__":
    main()
    print("Style fixes applied. Run flake8 or pylint again to check remaining issues.")
