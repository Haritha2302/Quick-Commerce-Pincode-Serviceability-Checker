from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Desired capabilities
desired_caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "emulator-5554",
    "appPackage": "com.zeptoconsumerapp",
    "appActivity": "com.zeptoconsumerapp.ui.splash.SplashActivity",
    "noReset": True
}

# Setup
try:
    driver = webdriver.Remote("http://127.0.0.1:4723", desired_caps)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 15)
except Exception as e:
    print(f"❌ Failed to start Appium session: {e}")
    exit(1)

pincode = "562110"

# Step 1: Open change address screen
try:
    print("📍 Waiting for change address button...")
    change_button = wait.until(EC.element_to_be_clickable(
        (AppiumBy.ID, "com.zeptoconsumerapp:id/select-your-location-manually")
    ))
    print("✅ Found change address button. Clicking...")
    change_button.click()
except Exception as e:
    print(f"❌ Failed at Step 1 (Change Address): {e}")
    driver.quit()
    exit(1)

# Step 2: Enter pincode
try:
    print("📍 Entering pincode...")
    pincode_input = wait.until(EC.presence_of_element_located(
        (AppiumBy.ID, "com.zeptoconsumerapp:id/search-new-address-test-input")
    ))
    pincode_input.click()
    pincode_input.send_keys(pincode)
    time.sleep(2)
except Exception as e:
    print(f"❌ Failed at Step 2 (Pincode Entry): {e}")
    driver.quit()
    exit(1)

# Step 3: Select first address option
try:
    print("📍 Selecting first location option...")
    location_options = wait.until(EC.presence_of_all_elements_located(
        (AppiumBy.CLASS_NAME, "android.view.ViewGroup")
    ))
    if len(location_options) > 1:
        location_options[1].click()
    else:
        raise Exception("No address options found.")
except Exception as e:
    print(f"❌ Failed at Step 3 (Select Address): {e}")
    driver.quit()
    exit(1)

# Step 4: Confirm selection
try:
    print("📍 Confirming selected address...")
    confirm_btn = wait.until(EC.element_to_be_clickable(
        (AppiumBy.ACCESSIBILITY_ID, "Confirm & Continue")
    ))
    confirm_btn.click()
except Exception as e:
    print(f"❌ Failed at Step 4 (Confirm Selection): {e}")
    driver.quit()
    exit(1)

# Step 5: Check serviceability result
try:
    print("📍 Checking if pincode is serviceable...")
    time.sleep(4)  # Allow result screen to settle

    not_serviceable = driver.find_elements(AppiumBy.ID, "00000000-0000-0003-ffff-ffff000003b2")
    if not_serviceable:
        print(f"❌ Pincode {pincode} is NOT serviceable")
    else:
        serviceable = driver.find_elements(AppiumBy.ID, "00000000-0000-0003-ffff-ffff00000515")
        if serviceable:
            print(f"✅ Pincode {pincode} is serviceable")
        else:
            print("⚠️ Could not determine serviceability status.")
except Exception as e:
    print(f"❌ Failed at Step 5 (Check Result): {e}")
finally:
    driver.quit()
