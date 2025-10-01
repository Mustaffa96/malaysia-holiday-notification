#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


def check_website_structure():
    url = "https://www.officeholidays.com/countries/malaysia"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='country-table')

        if not table:
            print("Could not find holiday table on the website")
            return

        rows = table.find_all('tr')[1:10]  # Get first few rows for analysis

        print("Sample holiday data from website:")
        print("-" * 60)

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                date_str = cols[0].get_text(strip=True)
                day = cols[1].get_text(strip=True)
                name = cols[2].get_text(strip=True)

                print(f"Date text: '{date_str}'")
                print(f"Day: '{day}'")
                print(f"Holiday name: '{name}'")
                print("-" * 40)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_website_structure()
