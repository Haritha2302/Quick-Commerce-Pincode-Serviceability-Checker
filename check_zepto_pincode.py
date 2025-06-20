from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

# Desired capabilities
desired_caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "emulator-5554",
    "appPackage": "com.zeptoconsumerapp",
    "appActivity": "com.zeptoconsumerapp.ui.splash.SplashActivity",
    "noReset": True
}

# Connect to Appium
driver = webdriver.Remote("http://127.0.0.1:4723", desired_caps)
driver.implicitly_wait(10)

# Step 1: Open change address screen
print("📍 Launching Zepto and waiting for change address button...")  # Logging
wait = WebDriverWait(driver, 15)  # 15 seconds max

change_button = wait.until(EC.element_to_be_clickable(
    (AppiumBy.ID, "com.zeptoconsumerapp:id/select-your-location-manually")
))

print("✅ Found change address button. Clicking...")  # Logging
change_button.click()

# Step 2: Enter pincode
print("Wait Step 2")  # Logging
wait = WebDriverWait(driver, 15)  # 15 seconds max

pincode = "562110"
pincode_input = driver.find_element(AppiumBy.ID, "com.zeptoconsumerapp:id/search-new-address-test-input")
pincode_input.click()
pincode_input.send_keys(pincode)
time.sleep(2)
print("Complete Step 2")  # Logging

# Step 3: Select first location option (ViewGroup index 1)
print("Wait Step 3")  # Logging
wait = WebDriverWait(driver, 15)  # 15 seconds max

location_options = driver.find_elements(AppiumBy.CLASS_NAME, "android.view.ViewGroup")
if len(location_options) > 1:
    location_options[1].click()
else:
    print("❌ No location options found.")
    driver.quit()
    exit()
print("Complete Step 3")  # Logging

# Step 4: Tap confirm button
print("Wait Step 4")  # Logging
wait = WebDriverWait(driver, 15)  # 15 seconds max

confirm_btn = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Confirm & Continue")
confirm_btn.click()
print("Complete Step 4")  # Logging

# Step 5: Check serviceability
print("Wait Step 5")  # Logging
wait = WebDriverWait(driver, 15)  # 15 seconds max

not_serviceable = driver.find_elements(AppiumBy.ID, "00000000-0000-0003-ffff-ffff000003b2")
if not_serviceable:
    print(f"❌ Pincode {pincode} is NOT serviceable")
else:
    serviceable = driver.find_elements(AppiumBy.ID, "00000000-0000-0003-ffff-ffff00000515")
    if serviceable:
        print(f"✅ Pincode {pincode} is serviceable")
    else:
        print("⚠️ Could not determine serviceability status")

driver.quit()
