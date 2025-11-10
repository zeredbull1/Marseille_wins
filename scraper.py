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
import os

# Setup Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def team_matches_scraper(url,team):
    # URL to scrape
    driver.get(url)

    time.sleep(3)

    cloudflare_count = 0
    max_cloudflare_attempts = 3

    while "Just a moment" in driver.title and cloudflare_count < max_cloudflare_attempts:
        print(f"Cloudflare detected ({cloudflare_count+1}/{max_cloudflare_attempts}), waiting longer...")
        time.sleep(3)
        cloudflare_count += 1

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table#matchlogs_for"))
    )

    table = driver.find_element(By.CSS_SELECTOR, "table#matchlogs_for")

    rows = table.find_elements(By.CSS_SELECTOR, "tr[data-row]")

    matches = []

    for row in rows:
        try:
            if "divider" in row.get_attribute("class"):
                continue

            date_element = row.find_element(By.CSS_SELECTOR, "th[data-stat='date']")
            date_text = date_element.text.strip()
            
            venue_element = row.find_element(By.CSS_SELECTOR, "td[data-stat='venue']")
            venue_text = venue_element.text.strip()
            
            opponent_element = row.find_element(By.CSS_SELECTOR, "td[data-stat='opponent']")
            opponent_text = opponent_element.text.strip()
            
            match_date = datetime.strptime(date_text, "%Y-%m-%d")
            
            # Add match data
            match_data = {
                'date': match_date,
                'team': team,
                'venue_team': venue_text,
                'opponent': opponent_text
            }
            
            print(f"Extracted match: {match_date} - {venue_text} - {opponent_text}")
            matches.append(match_data)
        except Exception as e :
            print(f"erorr with this row: {e}")



    df = pd.DataFrame(matches)

    # Sort by date and calculate rest days
    df = df.sort_values('date')
    df[f'rest_days_{team}'] = (df['date'] - df['date'].shift(1)).dt.days
    df[f'rest_days_{team}'] = df[f'rest_days_{team}'].fillna(0).astype(int)

    print("\nExtracted data:")
    print(df)

    # Save to CSV
    output_file = f'data/{team}_matches_with_rest_days_2024.csv'
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

Ligue1_teams_2024 = {
    "Paris-Saint-Germain" : "https://fbref.com/en/squads/e2d8892c/2024-2025/matchlogs/all_comps/schedule/Paris-Saint-Germain-Scores-and-Fixtures-All-Competitions",
    "Marseille" : "https://fbref.com/en/squads/5725cc7b/2024-2025/matchlogs/all_comps/schedule/Marseille-Scores-and-Fixtures-All-Competitions",
    "Monaco" : "https://fbref.com/en/squads/fd6114db/2024-2025/matchlogs/all_comps/schedule/Monaco-Scores-and-Fixtures-All-Competitions",
    "Nice" : "https://fbref.com/en/squads/132ebc33/2024-2025/matchlogs/all_comps/schedule/Nice-Scores-and-Fixtures-All-Competitions",
    "Lille" : "https://fbref.com/en/squads/cb188c0c/2024-2025/matchlogs/all_comps/schedule/Lille-Scores-and-Fixtures-All-Competitions",
    "Lyon" : "https://fbref.com/en/squads/d53c0b06/2024-2025/matchlogs/all_comps/schedule/Lyon-Scores-and-Fixtures-All-Competitions",
    "Strasbourg" : "https://fbref.com/en/squads/c0d3eab4/2024-2025/matchlogs/all_comps/schedule/Strasbourg-Scores-and-Fixtures-All-Competitions",
    "Lens" : "https://fbref.com/en/squads/fd4e0f7d/2024-2025/matchlogs/all_comps/schedule/Lens-Scores-and-Fixtures-All-Competitions",
    "Rennes" : "https://fbref.com/en/squads/b3072e00/2024-2025/matchlogs/all_comps/schedule/Rennes-Scores-and-Fixtures-All-Competitions",
    "Toulouse" : "https://fbref.com/en/squads/3f8c4b5f/2024-2025/matchlogs/all_comps/schedule/Toulouse-Scores-and-Fixtures-All-Competitions",
    "Brest" : "https://fbref.com/en/squads/fb08dbb3/2024-2025/matchlogs/all_comps/schedule/Brest-Scores-and-Fixtures-All-Competitions",
    "Le-Havre" : "https://fbref.com/en/squads/5c2737db/2024-2025/matchlogs/all_comps/schedule/Le-Havre-Scores-and-Fixtures-All-Competitions",
    "Nantes" : "https://fbref.com/en/squads/d7a486cd/2024-2025/matchlogs/all_comps/schedule/Nantes-Scores-and-Fixtures-All-Competitions",
    "Auxerre" : "https://fbref.com/en/squads/5ae09109/2024-2025/matchlogs/all_comps/schedule/Auxerre-Scores-and-Fixtures-All-Competitions",
    "Angers" : "https://fbref.com/en/squads/69236f98/2024-2025/matchlogs/all_comps/schedule/Angers-Scores-and-Fixtures-All-Competitions",
    "Reims" : "https://fbref.com/en/squads/7fdd64e0/2024-2025/matchlogs/all_comps/schedule/Reims-Scores-and-Fixtures-All-Competitions",
    "Montpellier" : "https://fbref.com/en/squads/281b0e73/2024-2025/matchlogs/all_comps/schedule/Montpellier-Scores-and-Fixtures-All-Competitions",
    "Saint-Etienne" : "https://fbref.com/en/squads/d298ef2c/2024-2025/matchlogs/all_comps/schedule/Saint-Etienne-Scores-and-Fixtures-All-Competitions"
}

for team, url in Ligue1_teams_2024.items():
    team_matches_scraper(url, team)


