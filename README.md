# 🧾 Pincode Serviceability Checker

Check whether a list of Indian pincodes is serviceable on **Zepto** and **Blinkit** using automated browser checks via Selenium.

---

## 🚀 Features

* Accepts CSV input with a list of pincodes
* Validates and filters incorrect pincodes
* Checks:

  * **Zepto** by entering the pincode, selecting a matching address, and detecting serviceability via presence of a **"Sit Tight! We’re Coming Soon!"** message
  * **Blinkit** by entering the pincode and selecting the address, and checking for a non-serviceable element
* Outputs:

  * `serviceability_results.csv` – status for each pincode
  * `invalid_pincodes.csv` – any entries that were invalid

---

## 🗂 Input Format

Create a CSV named `pincodes.csv` in the same folder:

```
562110
500032
123456
notapincode
```

Only 6-digit numeric entries will be processed.

---

## 🧪 Output Files

* `serviceability_results.csv`

  | Pincode | Address        | Zepto       | Blinkit         |
  | ------- | -------------- | ----------- | --------------- |
  | 562110  | Devanahalli... | Serviceable | Not Serviceable |

* `invalid_pincodes.csv`
  List of skipped/invalid pincodes.

---

## 🧰 Requirements

* Python 3.7+
* Chrome browser installed
* [ChromeDriver](https://sites.google.com/chromium.org/driver/) matching your Chrome version
* Python packages:

  ```bash
  pip install selenium
  ```

---

## 🧾 Usage

```bash
python3 check_serviceability.py
```

* Chrome will open automatically for each pincode and check both services one by one.
* Browser is maximized for visibility (not headless).

---

## 🔍 How Serviceability is Detected

### Zepto

* Pincode is entered in the location search box.
* First result is selected.
* **Confirm & Continue** is clicked.
* If a message containing **"Sit Tight! We’re Coming Soon!"** is found, the pincode is **Not Serviceable**.
* Otherwise, marked as **Serviceable**.

### Blinkit

* Pincode is entered in the location popup.
* First matching result is clicked.
* If a **non-serviceable element** is detected, it's **Not Serviceable**.
* Otherwise, **Serviceable**.

---

## 🧪 Debugging Tips

* If Zepto fails:

  * Ensure popups or location permissions aren’t blocking input.
  * You can add `print()` statements inside `check_zepto()` to trace.
* If Blinkit fails:

  * Check that address container loads – add waits if needed.

---

## ✅ To Do / Improvements

* Add retry on timeout or click failures
* Add support for more services
* Optional: Run headless for faster batch processing

---
