import requests
from bs4 import BeautifulSoup
import pandas as pd
import certifi
from datetime import datetime
import os
import ssl
import urllib3

print(f"Connecting to: {https://earthquake.phivolcs.dost.gov.ph/}")
print(f"Response status: {response.status_code}")
print(response.text[:500])  # Preview HTML

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_phivolcs():
    url = "https://earthquake.phivolcs.dost.gov.ph/"
    headers = {
        "User-Agent": "Microsoft Edge/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=certifi.where())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')

        if not table:
            raise ValueError("No earthquake table found on the page.")

        rows = table.find_all('tr')[1:]
        data = []
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) != 7:
                print(f"Skipping row {i} due to unexpected column count.")
                continue
            data.append([col.text.strip() for col in cols])

        columns = ['Date', 'Time', 'Latitude', 'Longitude', 'Depth', 'Magnitude', 'Location']
        df = pd.DataFrame(data, columns=columns)

        # Optional: Add timestamp
        df['Scraped_At'] = pd.Timestamp.now()

        # Optional: Deduplicate
        if os.path.exists('phivolcs_earthquakes.csv'):
            old_df = pd.read_csv('phivolcs_earthquakes.csv')
            df = pd.concat([old_df, df]).drop_duplicates().reset_index(drop=True)

        df.to_csv('phivolcs_earthquakes.csv', index=False)
        print(f"Scraped {len(df)} records successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_phivolcs()
