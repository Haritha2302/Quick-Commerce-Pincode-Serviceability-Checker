# 🧭 Pincode Serviceability Checker

This tool automates serviceability checks for Indian grocery delivery platforms — **Zepto**, **Blinkit**, and **Instamart (Swiggy)** — using Selenium.

It reads a list of Indian pincodes from a CSV file and returns whether grocery delivery is supported on each platform, along with the detected address (if available).

---

## 📦 What It Does

- Validates each input pincode.
- Checks service availability across:
  - 🛒 Zepto (`https://www.zeptonow.com`)
  - ⚡ Blinkit (`https://www.blinkit.com`)
  - 🥫 Instamart (via `https://www.swiggy.com`)
- Captures:
  - Serviceability status: `Serviceable`, `Not Serviceable`, `Invalid or No Match`, `Error`, `Unconfirmed`
  - Displayed address for each successful match
- Outputs results in CSV files.

---

## 🛠️ How to Run

### 1. 📥 Prepare Input

Create a file named `pincodes.csv` with one pincode per line:

```
682306
500032
A77H90
```

There is a file titled 'pincodes.csv' in this project you can use to test.
Only valid 6-digit numeric pincodes will be processed.

### 2. 🧪 Set Up Environment

Make sure you have:

- Python 3.x
- Google Chrome installed
- Compatible [ChromeDriver](https://sites.google.com/chromium.org/driver/) added to your system PATH

Install required Python libraries:

```bash
pip install -r requirements.txt
```

### 3. 🚀 Run the Script

```bash
python3 pincode_serviceability_check.py
```

### 4. 📁 Output

- `serviceability_results.csv` — main results with status and address
- `invalid_pincodes.csv` — list of invalid or malformed pincodes

---

## 📌 Why Some Design Decisions Were Made

### 🔁 Separate Browser Sessions for Each Check

Instamart (Swiggy) changes the page context based on address selection — sometimes redirecting to `/restaurants`. Reloading doesn't reset this reliably, so we restart the browser for each platform to ensure test consistency and clean sessions.

### ⚠️ “Unconfirmed” Status for Instamart

Swiggy’s UX doesn't always make serviceability clear. If no banners or known error messages appear, the status is marked `Unconfirmed` as a fallback.

---

## 📥 Inputs

- `pincodes.csv` — required input file with one pincode per line

---

## 📤 Outputs

| Column      | Description                              |
|-------------|------------------------------------------|
| Pincode     | 6-digit pincode checked                  |
| Address     | Detected address (from any platform)     |
| Zepto       | `Serviceable`, `Not Serviceable`, etc.   |
| Blinkit     | Same as above                            |
| Instamart   | Same as above                            |

---

## 🧠 Notes

- Script waits intelligently for page elements to appear.
- Includes fallback handling for flaky or slow-loading pages.
- Errors and skipped entries are handled gracefully with logging.

---

## 🧹 Troubleshooting

- **StaleElementReferenceException**: Zepto is dynamic; we refetch elements to avoid this, but it may still occasionally occur. The retry mechanism helps reduce this risk.
- **Blinkit/Instamart shows “Not Serviceable” even when known to work**: UI inconsistencies may cause false negatives — retrying or using a fresh session can help.

---

## 📃 License

MIT License – free to use, modify, and share.
