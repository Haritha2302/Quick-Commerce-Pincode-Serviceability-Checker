# pincode_serviceability_check.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
import time
import csv


def check_zepto_pincode_serviceability(driver, wait, pincode):
    try:
        print(f"\n🔍 Checking pincode: {pincode}")

        # Step 1: Click "Select Location"
        for attempt in range(2):
            try:
                location_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[@aria-label="Select Location"]')
                ))
                location_btn.click()
                break
            except ElementClickInterceptedException:
                print(f"⚠️ Retry {attempt+1}: Couldn't click 'Select Location': ElementClickInterceptedException")
                time.sleep(1)
        else:
            raise Exception("Select Location button not clickable")

        # Step 2: Enter Pincode
        input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]')))
        input_field.clear()
        input_field.send_keys(pincode)

        # Step 3: Select first address
        options = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-testid="address-search-item"]')
        ))
        if not options:
            print(f"❌ No address suggestions for pincode {pincode}")
            return {
                "pincode": pincode,
                "address": None,
                "zepto": "Invalid or No Match",
                "blinkit": "", "instamart": "", "bigbasket": "", "flipkart": "", "amazon": ""
            }

        options[0].click()
        print("✅ Address selected.")

        # Step 4: Confirm
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="location-confirm-btn"]'))).click()

        # Step 5: Wait for homepage update
        address_text = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-address"] span'))
        ).text
        print(f"🏠 Final address: {address_text}")

        # Step 6: Check serviceability
        time.sleep(3)
        unserviceable_msg = driver.find_elements(By.XPATH,
            '//h3[contains(text(), "Sit Tight")] | //img[contains(@src, "unserviceable-graphic.png")]')
        
        if unserviceable_msg:
            print(f"❌ Pincode {pincode} is NOT serviceable.")
            status = "Not Serviceable"
        elif driver.find_elements(By.CSS_SELECTOR, '[data-testid="delivery-time"]'):
            print(f"✅ Pincode {pincode} is serviceable.")
            status = "Serviceable"
        else:
            print(f"⚠️ Status unknown for pincode {pincode}")
            status = "Unknown"

        return {
            "pincode": pincode,
            "address": address_text,
            "zepto": status,
            "blinkit": "", "instamart": "", "bigbasket": "", "flipkart": "", "amazon": ""
        }

    except Exception as e:
        print(f"❌ Error checking pincode {pincode}: {e}")
        return {
            "pincode": pincode,
            "address": None,
            "zepto": "Error",
            "blinkit": "", "instamart": "", "bigbasket": "", "flipkart": "", "amazon": ""
        }


def read_pincodes_from_csv(filename):
    valid = []
    invalid = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            code = row.get("pincode", "").strip()
            if code.isdigit() and len(code) == 6:
                valid.append(code)
            else:
                print(f"⚠️ Skipping invalid pincode: {code}")
                invalid.append({"pincode": code})
    return valid, invalid


def save_invalid_pincodes(invalid_list, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["pincode"])
        writer.writeheader()
        for row in invalid_list:
            writer.writerow(row)


def save_results_to_csv(results, filename):
    fieldnames = ["pincode", "address", "zepto", "blinkit", "instamart", "bigbasket", "flipkart", "amazon"]
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    input_file = "pincodes.csv"
    output_file = "pincode_serviceability.csv"
    invalid_output_file = "invalid_pincodes.csv"
    print(f"\nStarting")

    pincodes, invalids = read_pincodes_from_csv(input_file)
    save_invalid_pincodes(invalids, invalid_output_file)

    results = []
    print(f"\n✅ Read pincodes {pincodes}")

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.zeptonow.com/")

    for pincode in pincodes:
        result = check_zepto_pincode_serviceability(driver, wait, pincode)
        results.append(result)
        time.sleep(2)  # optional delay

    print("\n📋 Final Report:")
    for r in results:
        print(f"{r['pincode']} → {r['zepto']} | {r['address'] or 'N/A'}")

    save_results_to_csv(results, output_file)
    print(f"\n✅ Results saved to {output_file}")
    print(f"🗂️  Invalid pincodes saved to {invalid_output_file}")

    input("\n🛑 Press Enter to close browser...")
    driver.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
