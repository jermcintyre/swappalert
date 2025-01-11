# SwappAlert

SwappAlert is a Python script designed to monitor and analyze listings for any device on [Swappa](https://swappa.com). Stay informed about the latest deals by dynamically tracking and displaying listings under your specified budget.

## Features
- Monitors listings under a specified price threshold.
- Highlights listings significantly below the average price using dynamic thresholds (e.g., standard deviations).
- Displays the cheapest listings for each condition (`New`, `Mint`, `Good`, `Fair`) and storage size.
- Fully customizable to your preferences.

## Requirements
- Python 3.8 or later
- Google Chrome
- Chromedriver
- The following Python libraries:
  - selenium
  - webdriver-manager
  - rich

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/[your-username]/swappalert.git
   cd swappalert
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Edit the script (`swappalert.py`) to configure your `MAX_PRICE` and other preferences.

## Usage
Run the script:
```bash
python swappalert.py
```

## Configuration
Customize these key variables in the script:
- **MAX_PRICE**: Set your budget to filter listings.
- **SIGNIFICANCE_STD_DEV_MULTIPLIER**: Adjust the dynamic threshold for flagging significantly cheaper listings (e.g., `1.5` standard deviations below the mean).

## Example Output
SwappAlert displays three tables:
1. **Listings Under Budget**  
   All listings that match your budget criteria.
2. **Significant Listings**  
   Listings significantly cheaper than the average price.
3. **Cheapest Listings by Condition and Size**  
   The cheapest listings for each condition and storage size.

Sample output:
```
       Cheapest Listings by Condition and Size (Sorted)
┌────────────┬──────────────┬────────────┬────────────────────────────────┐
│ Price ($)  │ Condition    │ Size (GB)  │ Link                           │
├────────────┼──────────────┼────────────┼────────────────────────────────┤
│ 699        │ New          │ 128 GB     │ https://swappa.com/listing/... │
│ 720        │ Mint         │ 256 GB     │ https://swappa.com/listing/... │
└────────────┴──────────────┴────────────┴────────────────────────────────┘
```

## License
SwappAlert is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request.

## Disclaimer
SwappAlert is for informational purposes only. The script interacts with the Swappa website by automating browser navigation. Use responsibly and ensure compliance with Swappa's terms of service.

