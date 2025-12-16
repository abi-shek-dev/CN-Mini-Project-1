import pandas as pd
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

COIN_MARKET_CAP_URL = 'https://coinmarketcap.com/'
OUTPUT_FILENAME = 'crypto_prices_log.csv'
MAX_COINS = 10 

def get_driver(headless=True):
    print("Initializing Chrome Driver...")
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_coin_data(row):
    try:
        rank = row.find_element(By.XPATH, './td[2]').text.split('\n')[0].strip()
        
        name_block = row.find_element(By.XPATH, './td[3]').text.split('\n')
        name = name_block[0].strip()
        symbol = name_block[1].strip() if len(name_block) > 1 else 'N/A'
        
        try:
            price = row.find_element(By.XPATH, './td[4]//span').text
        except:
            price = row.find_element(By.XPATH, './td[4]').text

        change_24h = row.find_element(By.XPATH, './td[6]').text 
        
        market_cap = row.find_element(By.XPATH, './td[8]').text

        return {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Rank': rank,
            'Name': name,
            'Symbol': symbol,
            'Price': price,
            '24h_Change': change_24h,
            'Market_Cap': market_cap,
        }
    except Exception as e:
        return None

def scrape_market_data(driver):
    print(f"Accessing {COIN_MARKET_CAP_URL}...")
    driver.get(COIN_MARKET_CAP_URL)
    
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cmc-table")))
        time.sleep(3) 
        driver.execute_script("window.scrollTo(0, 500);")
    except:
        print("Timeout waiting for table.")
        return []

    rows = driver.find_elements(By.XPATH, '//table/tbody/tr')
    print(f"Detected {len(rows)} rows. Processing top {MAX_COINS}...")

    results = []
    for i, row in enumerate(rows[:MAX_COINS]):
        data = extract_coin_data(row)
        if data:
            results.append(data)
            print(f"--> [{data['Rank']}] {data['Name']} | Cap: {data['Market_Cap']}")
            
    return results

def save_data(data_list):
    if not data_list:
        print("No data extracted.")
        return

    df = pd.DataFrame(data_list)
    
    for col in ['Price', 'Market_Cap']:
        df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)

    header_needed = not os.path.exists(OUTPUT_FILENAME)
    df.to_csv(OUTPUT_FILENAME, mode='a', header=header_needed, index=False)
    print(f"\nSaved {len(df)} records to {OUTPUT_FILENAME}")

def main():
    driver = None
    try:
        driver = get_driver(headless=True)
        data = scrape_market_data(driver)
        save_data(data)
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()