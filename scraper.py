import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)

url = "https://fbref.com/en/squads/5725cc7b/2024-2025/matchlogs/all_comps/misc/Marseille-Match-Logs-All-Competitions"

driver.get(url)

time.sleep(10) # Giving time to cloudfare to process

while "Just a moment" in driver.title:
        print("Still on Cloudflare page, waiting longer...")
        time.sleep(15)

WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#matchlogs_for"))
        )
        
# Extract the table
table = driver.find_element(By.CSS_SELECTOR, "table#matchlogs_for")
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

matches = []

for row in rows:
    try:
        # Skip rows without actual match data
        cells = row.find_elements(By.TAG_NAME, "th")
        if not cells or "divider" in row.get_attribute("class"):
            continue
        
        # Extract date 
        date_element = row.find_element(By.CSS_SELECTOR, "th[data-stat='date']")
        date_text = date_element.text.strip()

        match_date = datetime.strptime(date_text, "%Y-%m-%d")

        matches.append({'date': match_date})
    
    except Exception as e:
        print(f"Error extracting match data: {e}")
        continue

df = pd.DataFrame(matches)
df['rest_days'] = df['date'] - df['date'].shift(1) # calculating day difference between current day and previous match day 
print(df)


output_file = 'data/marseille_matches_with_rest_days_2024.csv'
df.to_csv(output_file, index=False)


