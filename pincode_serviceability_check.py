import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def read_valid_pincodes_from_csv(input_csv):
    valid_pincodes = []
    invalid_pincodes = []
    with open(input_csv, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            pincode = row[0].strip()
            if pincode.isdigit() and len(pincode) == 6:
                valid_pincodes.append(pincode)
            else:
                invalid_pincodes.append(pincode)
    return valid_pincodes, invalid_pincodes

def write_results_to_csv(results, filename):
    fieldnames = ["Pincode", "Address", "Zepto", "Blinkit"]
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in results:
            writer.writerow(entry)

def write_invalid_pincodes(invalid_pincodes, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Invalid Pincode"])
        for pincode in invalid_pincodes:
            writer.writerow([pincode])

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)

def check_zepto(pincode):
    driver = setup_driver()
    status = "Error"
    address = "N/A"
    try:
        driver.get("https://www.zeptonow.com")
        wait = WebDriverWait(driver, 15)

        # Click the location button
        try:
            location_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@aria-label="Select Location"]')
            ))
            driver.execute_script("arguments[0].scrollIntoView(true);", location_button)
            time.sleep(0.5)
            location_button.click()
        except Exception as e:
            print(f"❌ Failed to click Zepto location button: {type(e).__name__} - {e}")
            return "Error", "N/A"

        # Enter pincode
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
        input_box.clear()
        input_box.send_keys(pincode)
        time.sleep(2)

        # Select address
        address_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="address-search-item"]')))
        if not address_list:
            return "Invalid or No Match", "N/A"

        first_address = address_list[0]
        driver.execute_script("arguments[0].scrollIntoView(true);", first_address)
        time.sleep(0.5)
        try:
            first_address.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", first_address)

        # Click confirm
        try:
            confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="location-confirm-btn"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            time.sleep(0.5)
            confirm_button.click()
        except Exception as e:
            print(f"⚠️ Could not click confirm: {type(e).__name__} - {e}")
            return "Error", "N/A"

        # Wait for page update and check for unserviceable banner
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Coming Soon')]")
            status = "Not Serviceable"
        except NoSuchElementException:
            status = "Serviceable"

        # Try to fetch current address
        try:
            address_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-address"]'))
            )
            address = address_elem.text
        except:
            address = "Serviceable, but address unknown"

    except Exception as e:
        print(f"❌ Unexpected Zepto error for {pincode}: {type(e).__name__} - {e}")
    finally:
        driver.quit()

    return status, address


def check_blinkit(pincode):
    driver = setup_driver()
    status = "Error"
    address = "N/A"
    try:
        driver.get("https://www.blinkit.com")
        wait = WebDriverWait(driver, 10)

        try:
            input_box = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "LocationSearchBox__InputSelect-sc-1k8u6a6-0"))
            )
        except TimeoutException:
            driver.quit()
            return "Error", "No input box"

        input_box.clear()
        input_box.send_keys(pincode)
        time.sleep(2)

        address_options = driver.find_elements(
            By.CLASS_NAME, "LocationSearchList__LocationListContainer-sc-93rfr7-0"
        )
        if not address_options:
            status = "Invalid or No Match"
        else:
            address_options[0].click()
            time.sleep(2)

            try:
                driver.find_element(By.CLASS_NAME, "non-serviceable-step")
                status = "Not Serviceable"
            except NoSuchElementException:
                status = "Serviceable"
                try:
                    address = driver.find_element(
                        By.CLASS_NAME, "LocationBar__Subtitle-sc-x8ezho-10"
                    ).text
                except:
                    address = "Unknown but serviceable"

    except Exception:
        pass
    finally:
        driver.quit()
    return status, address

def main():
    print("📦 Starting Pincode Serviceability Check...")
    input_csv = "pincodes.csv"
    output_csv = "serviceability_results.csv"
    invalid_csv = "invalid_pincodes.csv"

    valid_pincodes, invalid_pincodes = read_valid_pincodes_from_csv(input_csv)
    print(f"✅ Valid pincodes: {valid_pincodes}")
    print(f"⚠️ Invalid pincodes: {invalid_pincodes}")

    results = []
    for pincode in valid_pincodes:
        print(f"\n🔍 Checking pincode: {pincode}")

        zepto_status, zepto_address = check_zepto(pincode)
        print(f"🛒 Zepto: {zepto_status}")

        blinkit_status, blinkit_address = check_blinkit(pincode)
        print(f"⚡ Blinkit: {blinkit_status}")

        final_address = zepto_address if zepto_address != "N/A" else blinkit_address

        results.append({
            "Pincode": pincode,
            "Address": final_address,
            "Zepto": zepto_status,
            "Blinkit": blinkit_status,
        })

    write_results_to_csv(results, output_csv)
    write_invalid_pincodes(invalid_pincodes, invalid_csv)
    print(f"\n✅ All results saved to {output_csv}")
    print(f"🚫 Invalid pincodes saved to {invalid_csv}")

main()
