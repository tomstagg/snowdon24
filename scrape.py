from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json

driver_path = '/usr/local/bin/chromedriver'

chrome_options = Options()
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:

    driver.get('https://my.raceresult.com/298168/results')
    wait = WebDriverWait(driver, 10)
    show_all_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="show all 215 participants"]')))
    show_all_link.click()
    # show_all_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'aShowAll')))
    # show_all_button.click()
    time.sleep(1) # as javascript is async i think

    try: 
        cookie_banner = wait.until(EC.element_to_be_clickable((By.ID,'cookieChoiceDismiss')))
        cookie_banner.click()
    except Exception as e:
        print('no cookie banner found or unable to click', e)
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.MainTable.tablesorter.tablesorter-default" )))
    result_rows = table.find_elements(By.TAG_NAME,'tr')

    summary_keys = ["ignore", "place",  "bib", "class", "name", "gender","ag", "club", "laps", "time", "gap", "award", "ignore", "ignore"]
    ignore_summary_indices = [0, 12, 13]
    lap_keys = ["lap", "lap_time","total", "ignore","ignore", "ignore"]
    ignore_lap_indices = [3, 4, 5]


    data = []
    for row in result_rows:
        columns  = row.find_elements(By.TAG_NAME, 'td')
        row_data = [col.text for col in columns]
        results = {summary_keys[i]: row_data[i] for i in range(len(row_data)) if i not in ignore_summary_indices}

        # print(results)
        if len(row_data) > 1:
            row.click()
            details = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'divDetailsResults')))
            details_table = details.find_element(By.TAG_NAME,'table')
            details_rows = details_table.find_elements(By.TAG_NAME,'tr')

            laps = []
            for lap_detail in details_rows[1:-1]: # ignore 1st and last row
                lap_detail_columns = lap_detail.find_elements(By.TAG_NAME, 'td')
                lap_details_data = [lap_detail_column.text for lap_detail_column in lap_detail_columns]
                lap = {lap_keys[i]: lap_details_data[i] for i in range(len(lap_details_data)) if i not in ignore_lap_indices}
                if lap["lap_time"] != " ":
                    laps.append(lap)

            results["lap_details"] = laps
            close_details = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "imgDetailsClose")))
            close_details.click()
            time.sleep(1)
                                
        if results: 
            print(f"place={results['place']}, laps={results['laps']}, lap_details_count={len(results['lap_details'])}")
            data.append(results)

    with open("scraped_results.json", "w") as f:
        json.dump(data, f, indent=4)
    
except Exception as e:
    print("error", e)
    with open("scraped_results.json", "w") as f:
        json.dump(data, f, indent=4)
finally:
    driver.quit()

