from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from rich.table import Table
import time
import random
import statistics

# User configuration
SEARCH_URL = "https://swappa.com/listings/google-pixel-9-pro-xl?carrier=unlocked&color=&storage=&modeln=&condition=&sort=&exclude_businesses=on"
MAX_PRICE = 725
SIGNIFICANCE_STD_DEV_MULTIPLIER = 1.5  # Flag listings below this many standard deviations
CHECK_INTERVAL = 3  # Minutes

# List of User-Agent headers to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
]

# Initialize the console for rich output
console = Console()

def check_swappa():
    # Create tables for displaying listings
    table_all = Table(title="Swappa Listings Under Budget", title_style="bold cyan")
    table_all.add_column("Price ($)", style="bold green", justify="center")
    table_all.add_column("Size (GB/TB)", style="bold magenta", justify="center")
    table_all.add_column("Condition", style="bold yellow", justify="center")
    table_all.add_column("Link", style="bold blue", justify="left")
    
    table_significant = Table(title="Significant Listings (Dynamic Threshold)", title_style="bold red")
    table_significant.add_column("Price ($)", style="bold green", justify="center")
    table_significant.add_column("Size (GB/TB)", style="bold magenta", justify="center")
    table_significant.add_column("Condition", style="bold yellow", justify="center")
    table_significant.add_column("Link", style="bold blue", justify="left")
    
    table_cheapest = Table(title="Cheapest Listings by Condition and Size (Sorted)", title_style="bold green")
    table_cheapest.add_column("Price ($)", style="bold green", justify="center")
    table_cheapest.add_column("Condition", style="bold yellow", justify="center")
    table_cheapest.add_column("Size (GB/TB)", style="bold magenta", justify="center")
    table_cheapest.add_column("Link", style="bold blue", justify="left")

    # Randomize User-Agent for each request
    user_agent = random.choice(USER_AGENTS)
    console.log(f"Using User-Agent: {user_agent}")

    # Initialize Selenium WebDriver with random User-Agent
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load the page
        driver.get(SEARCH_URL)
        time.sleep(3)  # Wait for the page to load fully

        # Storage-size-wise and condition-wise grouping
        storage_prices = {}
        cheapest_by_condition_and_size = {}

        # Find all rows in the listing table
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")  # Adjust if necessary

        for row in rows:
            try:
                # Extract price
                price_element = row.find_element(By.CSS_SELECTOR, "strong.fs-6 span[itemprop='price']")
                price = float(price_element.text.strip())

                # Extract link
                link_element = row.find_element(By.CSS_SELECTOR, "a[aria-controls='slide_listing_update_price']")
                link = link_element.get_attribute("href")
                if not link.startswith("http"):
                    link = "https://swappa.com" + link

                # Extract size (GB/TB)
                try:
                    size_element = row.find_element(By.XPATH, ".//td[contains(text(),'GB') or contains(text(),'TB')]")
                    size = size_element.text.strip()
                except Exception:
                    size = "Unknown"

                # Extract condition (e.g., New, Mint, Good, Fair)
                try:
                    condition_element = row.find_element(By.XPATH, ".//td[contains(text(),'New') or contains(text(),'Mint') or contains(text(),'Good') or contains(text(),'Fair')]")
                    condition = condition_element.text.strip()
                except Exception:
                    condition = "Unknown"

                # Add to storage-specific grouping
                if size not in storage_prices:
                    storage_prices[size] = []
                storage_prices[size].append((price, condition, link))

                # Track cheapest listings by condition and size
                key = (size, condition)
                if key not in cheapest_by_condition_and_size or cheapest_by_condition_and_size[key][0] > price:
                    cheapest_by_condition_and_size[key] = (price, link)

                # Add to the "All Listings" table if under budget
                if price <= MAX_PRICE:
                    table_all.add_row(f"{price}", size, condition, f"[link={link}]{link}[/link]")
            except Exception:
                # Skip rows without a price, size, condition, or link
                continue

        # Analyze for dynamically significant prices
        for size, prices in storage_prices.items():
            all_prices = [p[0] for p in prices]
            if len(all_prices) > 1:  # Ensure we have enough data to calculate statistics
                avg_price = statistics.mean(all_prices)
                std_dev = statistics.stdev(all_prices)
                threshold_price = avg_price - (SIGNIFICANCE_STD_DEV_MULTIPLIER * std_dev)

                for price, condition, link in prices:
                    if price <= threshold_price:
                        table_significant.add_row(f"{price}", size, condition, f"[link={link}]{link}[/link]")

        # Sort cheapest listings by price
        sorted_cheapest = sorted(cheapest_by_condition_and_size.items(), key=lambda x: x[1][0])

        # Add sorted listings to the table
        for (size, condition), (price, link) in sorted_cheapest:
            table_cheapest.add_row(f"{price}", condition, size, f"[link={link}]{link}[/link]")

        # Display results
        console.clear()
        console.print(table_all)

        if len(table_significant.rows) > 0:
            console.print("\n")
            console.print(table_significant)
        else:
            console.print("\n[bold yellow]No significant listings found based on dynamic thresholds.[/bold yellow]")

        console.print("\n")
        console.print(table_cheapest)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

    finally:
        driver.quit()

while True:
    check_swappa()

    # Introduce a random delay between 55 and 65 seconds
    delay = random.randint(55, 65)
    console.log(f"Waiting for {delay} seconds before the next check...")
    time.sleep(delay)

