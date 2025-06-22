"""
Pincode Serviceability Checker for Zepto, Blinkit, and Instamart

📌 Key Design Decisions:
- Each service uses a new browser session to avoid state retention bugs (especially for Swiggy).
  - Swiggy Instamart redirects to restaurant listing if grocery is unavailable and does not reset reliably. Hence, fresh driver.
  - Zepto also occasionally fails with stale element references — isolated sessions help mitigate impact.
"""

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException,
    ElementClickInterceptedException, StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)


def read_valid_pincodes_from_csv(input_csv):
    valid, invalid = [], []
    with open(input_csv, newline="") as csvfile:
        for row in csv.reader(csvfile):
            pincode = row[0].strip()
            (valid if pincode.isdigit() and len(pincode) == 6 else invalid).append(pincode)
    return valid, invalid


def write_results_to_csv(results, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Pincode", "Address", "Zepto", "Blinkit", "Instamart"])
        writer.writeheader()
        writer.writerows(results)


def write_invalid_pincodes(invalid_pincodes, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Invalid Pincode"])
        for pincode in invalid_pincodes:
            writer.writerow([pincode])


def check_zepto(pincode):
    driver, status, address = setup_driver(), "Error", "N/A"
    try:
        driver.get("https://www.zeptonow.com")
        wait = WebDriverWait(driver, 15)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Select Location"]')))
            button = driver.find_element(By.XPATH, '//button[@aria-label="Select Location"]')
            button.click()
        except StaleElementReferenceException:
            button = driver.find_element(By.XPATH, '//button[@aria-label="Select Location"]')
            button.click()
        except Exception as e:
            print(f"❌ Zepto location button issue: {type(e).__name__} - {e}")
            return "Error", "N/A"

        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
        input_box.clear()
        input_box.send_keys(pincode)
        time.sleep(2)

        address_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="address-search-item"]')))
        if not address_list:
            return "Invalid or No Match", "N/A"

        try:
            address_list[0].click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", address_list[0])

        confirm_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="location-confirm-btn"]')))
        confirm_btn.click()

        time.sleep(3)
        status = "Not Serviceable" if driver.find_elements(By.XPATH, "//*[contains(text(), 'Coming Soon')]") else "Serviceable"

        try:
            address = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-address"]'))).text
        except:
            address = "Serviceable, but address unknown"

    except Exception as e:
        print(f"❌ Zepto error for {pincode}: {type(e).__name__} - {e}")
    finally:
        driver.quit()
    return status, address


def check_blinkit(pincode):
    driver, status, address = setup_driver(), "Error", "N/A"
    try:
        driver.get("https://www.blinkit.com")
        wait = WebDriverWait(driver, 10)

        input_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "LocationSearchBox__InputSelect-sc-1k8u6a6-0")))
        input_box.clear()
        input_box.send_keys(pincode)
        time.sleep(2)

        address_options = driver.find_elements(By.CLASS_NAME, "LocationSearchList__LocationListContainer-sc-93rfr7-0")
        if not address_options:
            return "Invalid or No Match", "N/A"

        address_options[0].click()
        time.sleep(2)

        if driver.find_elements(By.CLASS_NAME, "non-serviceable-step"):
            status = "Not Serviceable"
        else:
            status = "Serviceable"
            try:
                address = driver.find_element(By.CLASS_NAME, "LocationBar__Subtitle-sc-x8ezho-10").text
            except:
                address = "Unknown but serviceable"

    except Exception as e:
        print(f"⚠️ Blinkit error for {pincode}: {e}")
    finally:
        driver.quit()
    return status, address


def check_instamart(pincode):
    driver = setup_driver()
    result = {"status": "Invalid or No Match", "address": "N/A"}
    try:
        driver.get("https://www.swiggy.com/")
        wait = WebDriverWait(driver, 15)

        input_box = wait.until(EC.presence_of_element_located((By.ID, "location")))
        input_box.clear()
        input_box.send_keys(pincode)
        input_box.send_keys(Keys.RETURN)

        address_options = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "_2BgUI")))
        if not address_options:
            return result

        address = address_options[0].text.strip()
        address_options[0].click()
        time.sleep(5)

        if driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="navbar_container__2337995"]'):
            return {"status": "Serviceable", "address": address}

        if any("Location Unserviceable" in el.text for el in driver.find_elements(By.CLASS_NAME, "brPPUG")):
            return {"status": "Not Serviceable", "address": address}
        if any("services here" in el.text for el in driver.find_elements(By.CLASS_NAME, "ewYGxs")):
            return {"status": "Not Serviceable", "address": address}

        return {"status": "Unconfirmed", "address": address}

    except Exception as e:
        print(f"⚠️ Instamart error for {pincode}: {e}")
        result["status"] = "Error"
    finally:
        driver.quit()
    return result


def main():
    print("📦 Starting Pincode Serviceability Check...")
    input_csv = "pincodes.csv"
    output_csv = "serviceability_results.csv"
    invalid_csv = "invalid_pincodes.csv"

    valid_pins, invalid_pins = read_valid_pincodes_from_csv(input_csv)
    print(f"✅ Valid: {valid_pins}\n⚠️ Invalid: {invalid_pins}")

    results = []
    for pin in valid_pins:
        print(f"\n🔍 Checking: {pin}")
        zepto_stat, zepto_addr = check_zepto(pin)
        print(f"🛒 Zepto: {zepto_stat}")
        blinkit_stat, blinkit_addr = check_blinkit(pin)
        print(f"⚡ Blinkit: {blinkit_stat}")
        instamart = check_instamart(pin)
        print(f"🥫 Instamart: {instamart['status']}")

        address = next((a for a in [zepto_addr, blinkit_addr, instamart["address"]] if a != "N/A"), "N/A")
        results.append({
            "Pincode": pin,
            "Address": address,
            "Zepto": zepto_stat,
            "Blinkit": blinkit_stat,
            "Instamart": instamart["status"]
        })

    write_results_to_csv(results, output_csv)
    write_invalid_pincodes(invalid_pins, invalid_csv)
    print(f"\n✅ Done. Results: {output_csv} | Invalids: {invalid_csv}")


if __name__ == "__main__":
    main()
