# SwappAlert

SwappAlert notifies you when new or updated listings appear on Swappa that match your search criteria. It automatically checks for listings under your budget, flags deals priced significantly below average, and sends notifications to Discord. The script also organizes listings into detailed tables, making it easy to track prices and find the best options.

![image](https://github.com/user-attachments/assets/824bb245-a1d2-4af2-a2a6-2fcb6a21f40b)

---

## Features
- Monitors listings under a specified price threshold
- Sends Discord notifications for new listings and price updates
- Highlights listings significantly below average price using dynamic thresholds
- Displays the cheapest listings for each condition and storage size
- Fully customizable and user-friendly

---

## Requirements
- **Python**: 3.8 or later
- Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `rich`

---

## Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/jermcintyre/swappalert.git
cd swappalert
```

### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

### Swappa Search URL
1. Visit [Swappa](https://swappa.com) in your browser.
2. Use the search filters (e.g., condition, carrier, storage size) to find the device you're looking for.
3. Copy the URL with your desired filters and replace the `SEARCH_URL` variable in the script.

Example:
```python
SEARCH_URL = "https://swappa.com/listings/google-pixel-9-pro?carrier=unlocked&color=&storage=&modeln=&condition=&sort=&exclude_businesses=on"
```

### Key Variables
| Variable                      | Description                                                                                      | Default Value     |
|-------------------------------|--------------------------------------------------------------------------------------------------|-------------------|
| `MAX_PRICE`                   | The maximum price to consider for a listing (in USD).                                           | `610`             |
| `DESIRED_SIZE`                | Filters notifications for specific storage sizes (e.g., `"128 GB"`, `"256 GB"`, `"ANY"`).        | `"ANY"`           |
| `SIGNIFICANCE_STD_DEV_MULTIPLIER` | Flags listings significantly cheaper than average based on this number of standard deviations. | `1.5`             |
| `NOTIFICATION_INTERVAL`       | The time (in minutes) between Discord notifications.                                            | `5`               |
| `CACHE_CLEAR_HOURS`           | How long to keep notified listings in cache before clearing (in hours).                        | `24`              |

> **Note:** `DESIRED_SIZE` only affects Discord notifications. All sizes will still appear in the tables.

---

## Usage

### Running the Script
```bash
python3 swappalert.py
```

### Example Scenario
Looking for listings under **$500** with a storage size of **128 GB**:
1. Update the script:
   ```python
   MAX_PRICE = 500
   DESIRED_SIZE = "128 GB"
   ```
2. Run the script, and you’ll receive notifications for matching listings via Discord.

---

## Tables

SwappAlert displays three tables in your terminal:

1. **Listings Under Budget**  
   All listings that match your budget criteria.

2. **Significant Listings**  
   Listings significantly cheaper than the average price (based on statistical thresholds).

3. **Cheapest Listings by Condition and Size**  
   The cheapest listings for each condition (e.g., New, Mint, Good) and storage size.

---

## Discord Notifications
The script sends Discord notifications for:
- New listings that match your criteria.
- Price updates for previously notified listings.

Example notification:
```
🔔 New/Updated Swappa listings under budget:

💰 $610 | 128 GB | Mint
🔗 https://swappa.com/listing/view/LZAH19527

📊 PRICE UPDATE: $700 ➡️ $650 | 256 GB | Good
🔗 https://swappa.com/listing/view/LZAJ20941
```

---

## Docker Usage

### Build the Container
```bash
docker build -t swappalert .
```

### Run the Script in Docker
```bash
docker run -it swappalert
```

---

## License
SwappAlert is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing
We welcome contributions, issues, and feature requests! Fork the repository, make your changes, and submit a pull request.

---

## Disclaimer
SwappAlert is for informational purposes only. The script interacts with the Swappa website by automating browser navigation. Use responsibly and ensure compliance with Swappa's terms of service.
