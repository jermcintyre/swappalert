import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import time
import random
import statistics
import datetime

# User configuration
SEARCH_URL = "https://swappa.com/listings/google-pixel-9-pro?carrier=unlocked&color=&storage=&modeln=&condition=&sort=&exclude_businesses=on"  # Swappa search URL
MAX_PRICE = 610 # Maximum price to consider for a listing (in USD)
SIGNIFICANCE_STD_DEV_MULTIPLIER = 1.5  # Flag listings below this many standard deviations
CHECK_INTERVAL = 5  # Minutes
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1234567890/ABCDEFGHIJK"  # Discord webhook URL
NOTIFICATION_INTERVAL = 5  # Minutes
DESIRED_SIZE = "ANY"  # Desired size to filter notifications
CACHE_CLEAR_HOURS = 24  # Hours to keep listings in cache before clearing

# Initialize console for rich output
console = Console()

# Random User-Agent headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
]

# Notified listings cache
notified_listings = {}  # key: url, value: {price, size, condition, timestamp}
last_listings_clear = datetime.datetime.now()

# Discord notification function
def send_discord_notification(message: str):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            console.print(f"[bold red]Failed to send notification: {response.status_code}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Exception sending notification:[/bold red] {e}")

# Scrape Swappa listings
def scrape_swappa():
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    response = requests.get(SEARCH_URL, headers=headers)
    if response.status_code != 200:
        console.print(f"[bold red]Failed to fetch the Swappa page: {response.status_code}[/bold red]")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("tr")
    listings = []

    for row in rows:
        try:
            # Extract price
            price_element = row.select_one("strong.fs-6 span[itemprop='price']")
            if not price_element:
                continue
            price = float(price_element.text.strip())

            # Extract link
            link_element = row.select_one("a[href^='/listing/']")
            if not link_element:
                continue
            link = "https://swappa.com" + link_element.get("href")

            # Updated condition extraction - without HTML debug printing
            condition = "Unknown"
            for td in row.find_all("td"):
                text = td.text.strip()
                if any(c in text for c in ["New", "Mint", "Good", "Fair"]):
                    condition = next(c for c in ["New", "Mint", "Good", "Fair"] if c in text)
                    break

            # Extract size
            size_element = row.find(lambda tag: tag.name == "td" and ("GB" in tag.text or "TB" in tag.text))
            size = size_element.text.strip() if size_element else "Unknown"

            listings.append({"price": price, "size": size, "condition": condition, "link": link})
            
        except Exception as e:
            continue

    return listings

# Analyze listings and display results
last_notification_time = datetime.datetime.now() - datetime.timedelta(minutes=NOTIFICATION_INTERVAL)

def analyze_listings(listings):
    global last_notification_time, notified_listings, last_listings_clear
    now = datetime.datetime.now()

    # Clear old cache entries
    if (now - last_listings_clear).total_seconds() >= (CACHE_CLEAR_HOURS * 60 * 60):
        notified_listings.clear()
        last_listings_clear = now

    # Tables for each view
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

    table_cheapest = Table(title="Cheapest Listings by Condition and Size", title_style="bold green")
    table_cheapest.add_column("Price ($)", style="bold green", justify="center")
    table_cheapest.add_column("Condition", style="bold yellow", justify="center")
    table_cheapest.add_column("Size (GB/TB)", style="bold magenta", justify="center")
    table_cheapest.add_column("Link", style="bold blue", justify="left")

    # Storage-size-wise and condition-wise grouping
    storage_prices = {}
    cheapest_by_condition_and_size = {}

    for listing in listings:
        size = listing["size"]
        price = listing["price"]
        condition = listing["condition"]
        link = listing["link"]

        # Add to storage-specific grouping
        if size not in storage_prices:
            storage_prices[size] = []
        storage_prices[size].append(price)

        # Track cheapest listings by condition and size
        key = (size, condition)
        if key not in cheapest_by_condition_and_size or cheapest_by_condition_and_size[key][0] > price:
            cheapest_by_condition_and_size[key] = (price, link)

        # Add to "All Listings" table if under budget
        if price <= MAX_PRICE:
            table_all.add_row(f"{price}", size, condition, f"[link={link}]{link}[/link]")

    # Dynamically significant listings
    for size, prices in storage_prices.items():
        if len(prices) > 1:  # Ensure we have enough data to calculate statistics
            avg_price = statistics.mean(prices)
            std_dev = statistics.stdev(prices)
            threshold = avg_price - (SIGNIFICANCE_STD_DEV_MULTIPLIER * std_dev)
            for listing in listings:
                if listing["size"] == size and listing["price"] <= threshold:
                    table_significant.add_row(f"{listing['price']}", listing["size"], listing["condition"], f"[link={listing['link']}]{listing['link']}[/link]")

    # Add sorted cheapest listings to the table
    sorted_cheapest = sorted(cheapest_by_condition_and_size.items(), key=lambda x: x[1][0])
    for (size, condition), (price, link) in sorted_cheapest:
        table_cheapest.add_row(f"{price}", condition, size, f"[link={link}]{link}[/link]")

    # Display all tables
    console.clear()
    console.print(table_all)
    console.print("\n")
    console.print(table_significant)
    console.print("\n")
    console.print(table_cheapest)

    # Filter for new or updated listings
    matching_listings = [
        listing for listing in listings 
        if (listing['price'] <= MAX_PRICE and 
            (DESIRED_SIZE == "ANY" or listing['size'] == DESIRED_SIZE) and
            (listing['link'] not in notified_listings or 
             notified_listings[listing['link']]['price'] != listing['price']))
    ]
    
    if matching_listings and (now - last_notification_time).total_seconds() >= NOTIFICATION_INTERVAL * 60:
        message = "🔔 New/Updated Swappa listings under budget:\n\n"
        for listing in matching_listings:
            is_update = listing['link'] in notified_listings
            old_price = notified_listings.get(listing['link'], {}).get('price', None)
            
            if is_update:
                message += f"📊 PRICE UPDATE: ${old_price} ➡️ ${listing['price']} | {listing['size']} | {listing['condition']}\n"
            else:
                message += f"💰 ${listing['price']} | {listing['size']} | {listing['condition']}\n"
            message += f"🔗 {listing['link']}\n\n"
            
            # Update cache with new listing data
            notified_listings[listing['link']] = {
                'price': listing['price'],
                'size': listing['size'],
                'condition': listing['condition'],
                'timestamp': now
            }
        
        send_discord_notification(message)
        last_notification_time = now
        console.log(f"Discord notification sent for {len(matching_listings)} new/updated listings")

# Main function
def main():
    while True:
        listings = scrape_swappa()
        if listings:
            analyze_listings(listings)

        delay = random.randint(55, 65)
        console.log(f"Waiting {delay}s before next check...")
        time.sleep(delay)

if __name__ == "__main__":
    main()
