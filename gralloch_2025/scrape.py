import json
import time

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 1) Set up headless Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # comment out to see the browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

driver.get("https://www.grallochgravel.com/results")

# 2) Close cookie banner if present
try:
    btn = wait.until(
        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
    )
    btn.click()
    print("click on cookie button")
except TimeoutException:
    pass

time.sleep(5)
print("refresh page")
driver.refresh()


# 3) Define a “universal” row selector
ROW_CSS = "table.MainTable.tablesorter tbody[id^='tb_2Data'] tr"  # mens

# 4) Wait for the very first batch of rows
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ROW_CSS)))

# 5) Find the right “Show All” link
#    - grabs every <a class="aShowAll">, prints their text so you can confirm
links = driver.find_elements(By.CSS_SELECTOR, "a.aShowAll")
print("Found show-all links:", [link.text for link in links])

#    - pick the one whose text actually starts with “show all”
for link in links:
    if link.text.strip().lower().startswith("show all 174"):
        show_all = link
        break
else:
    raise RuntimeError("Could not find a “show all” link")

# # 6) Click it and wait for the row count to go up
driver.execute_script("arguments[0].scrollIntoView(true);", show_all)
before = len(driver.find_elements(By.CSS_SELECTOR, ROW_CSS))
print("Rows before expand:", before)

time.sleep(5)
show_all.click()
time.sleep(5)

try:
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ROW_CSS)) > before)
except TimeoutException:
    after = len(driver.find_elements(By.CSS_SELECTOR, ROW_CSS))
    raise RuntimeError(f"Timed out: still {after} rows, expected > {before}")

after = len(driver.find_elements(By.CSS_SELECTOR, ROW_CSS))
print("Rows after expand:", after)


table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.MainTable.tablesorter")))
# table_html = table.get_attribute("outerHTML")


data_rows = table.find_elements(
    By.XPATH, ".//tbody[@id='tb_2Data']//tr[td]"
)  # Only rows with <td> (skip headers)
print(f"{len(data_rows)=}")


def append_dict_to_file(d: dict, filename: str):
    # open in append mode
    with open(filename, "a", encoding="utf-8") as f:
        # serialize to JSON and write a new line
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


for row_index, row in enumerate(data_rows, start=1):
    results = {}
    cells = [td.text for td in row.find_elements(By.TAG_NAME, "td")]
    results["summary"] = cells
    print(row_index, cells)
    clickable = row.find_element(By.CSS_SELECTOR, "td")  # first cell
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", clickable)

    try:
        clickable.click()
    except ElementNotInteractableException:
        try:
            driver.execute_script("arguments[0].click();", clickable)
        except Exception:
            ActionChains(driver).move_to_element(clickable).click().perform()

    # row.click()
    # time.sleep(1)
    splits_inner = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.SplitsInner"))
    )
    # splits_inner = driver.find_element(By.CSS_SELECTOR, "div.SplitsInner")
    rows = splits_inner.find_elements(By.CSS_SELECTOR, ":scope > div >div")
    print(f"Found {len(rows)} rows")

    data_rows = rows[1:]

    details = []

    for i, row in enumerate(rows, 1):
        cells = row.find_elements(By.CSS_SELECTOR, ":scope > div")
        detail = [c.text for c in cells]
        details.append(detail)
        # print(f"Row {i}: {details}")

    results["details"] = details

    append_dict_to_file(results, "results.json")

    close_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "imgDetailsClose")))
    close_btn.click()

driver.quit()
