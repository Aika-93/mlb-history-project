""" 
MLB History Web Scraper
-------------------------------------------------------------------------------------------------------------------------------------
This script uses Selenium  to scrape historical MLB data
from the Major League Baseball history site and saves raw datasets as CSV files.

Datasets collected:
- All-Star Game results
- Award winners (MVP, Cy Young, Rookie of the Year)
- Team Managers history

Note:
The selected pages contain complete datasets in single tables,
so pagination handling is not required for these URLs.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
import pandas as pd
import time
import os

# ============================
# Create directories for data 
# ============================

#Create folders to store raw scraped data.
#exist_ok=True prevents errors if folders already exist.
os.makedirs("data", exist_ok=True)
os.makedirs("data/awards", exist_ok=True)

# ============================
# Configure Selenium WebDriver
# ============================

#Configure Chrome options to run in headless mode
#and mimic real browser using a custom user-agent
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

#Initialize Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# ====================================
# Scrape All-Star Game historical data 
# ====================================

def scrape_all_star_game(driver):
    driver.get("https://www.baseball-almanac.com/asgmenu.shtml")
    time.sleep(2) #Wait for page to load

    tables = driver.find_elements(By.TAG_NAME, "table")

    #Handle missing table scenario
    if not tables:
        print("No tables found on All-Star Game page")
        return
    
    data = []
    rows = tables[0].find_elements(By.TAG_NAME, "tr")

    #Skip header row
    for row in rows[1:]:   #Skip header row
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:  #Only include rows with all 5 columns
                data.append({
                    "Game": cols[0].text,
                    "Venue": cols[1].text,
                    "Date": cols[2].text,
                    "AL": cols[3].text,
                    "NL": cols[4].text
                })
        except Exception as e:
            #Skip malformed or empty rows and log the error
            print("Skipping row due to missing or malformed data:", e)
            continue

    df = pd.DataFrame(data)
    df.to_csv("data/all_star_game.csv", index=False)
    print("CSV saved: data/all_star_game.csv")

# ===================
# Scrape Awards data
# ===================
def scrape_award(driver, url, csv_name, columns=None):
    driver.get(url)
    time.sleep(2)

    tables = driver.find_elements(By.TAG_NAME, "table")

    if not tables:
        print(f"No tables found on {url}")
        return
    
    data = []
    rows = tables[0].find_elements(By.TAG_NAME, "tr")

    for row in rows[1:]:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if columns:  #If columns provided, use them
                if len(cols) >= len(columns):
                    data.append({columns[i]: cols[i].text for i in range(len(columns))})
                else:
                    print("Skipping row: not enough columns")
            else:  #Default scraping if columns not specified
                if len(cols) >= 5:
                    data.append({
                        "Year": cols[0].text,
                        "Name": cols[1].text,
                        "League": cols[2].text,
                        "Team": cols[3].text,
                        "Position": cols[4].text
                    })
                else:
                    print("Skipping row: not enough columns")
        except Exception as e:
            print("Skipping row due to error:", e)
            continue
    
    df = pd.DataFrame(data)
    df.to_csv(f"data/awards/{csv_name}.csv", index=False)
    print(f"CSV saved: data/awards/{csv_name}.csv")


# =========================
# Scrape Team Managers Data
# ========================= 

def scrape_managers(driver):
    driver.get("https://www.baseball-almanac.com/mgrmenu.shtml")
    time.sleep(2)

    tables = driver.find_elements(By.TAG_NAME, "table")

    if not tables:
        print("No tables found on Managers page")
        return

    data =[]

    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        for row in rows[1:]:  #Skip header row 
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    team = cols[0].text.strip()
                    manager_name = cols[1].text.strip()
                    years = cols[2].text.strip()
                    
                    #Skip rows with no manager or only dashes
                    if not manager_name or manager_name.replace("-", "").strip() == "":
                        continue  

                    data.append({
                        "Team": team,
                        "Manager": manager_name,
                        "Years": years
                    })
            except Exception as e:
                print("Skipping row due to missing data:", e)
                continue

    df = pd.DataFrame(data)
    df.to_csv("data/managers.csv", index=False)
    print("CSV saved: data/managers.csv")


# ======================
# Run Scraping Process
# ======================

#All-Star Game
scrape_all_star_game(driver)

#Awards
scrape_award(
    driver,
    "https://www.baseball-almanac.com/awards/aw_mvpa.shtml",
    "all_star_mvp_award",
    columns=["Year", "Name", "League", "Team", "Position"]
)

scrape_award(
    driver,
    "https://www.baseball-almanac.com/awards/aw_cyy.shtml",
    "cy_young_award",
    columns=["Year", "League", "Name", "Team", "TH", "W-L", "ERA", "IP", "SO", "SV"]
)

scrape_award(
    driver,
    "https://www.baseball-almanac.com/awards/aw_roy.shtml",
    "rookie_of_the_year_award",
    columns=["Year", "League", "Name", "Team", "Position"]
)

#Managers
scrape_managers(driver)

#Close the browser after scraping
driver.quit()
print("Scraping finished")