import os, sys, arrow

from download import ZendeskDownloader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

email_address = os.getenv("ZENDESK_EMAIL_ADDRESS")
api_token = os.getenv("ZENDESK_API_TOKEN")

# Headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# Combine email and API token for basic authentication
auth = (f'{email_address}/token', api_token)

print('Downloading English articles')

# Prompt user for download option
print("Choose download option:")
print("1: Download all articles")
print("2: Download articles written/updated after a specific date and time")
download_option = input("Enter your choice (1 or 2): ").strip()

if download_option == "1":
    time = 0
elif download_option == "2":
    # Prompt user for date and time
    print("Please enter the date and time in Taiwan's timezone (CST).")
    date_str = input("Enter the date (YYYY-MM-DD): ").strip()
    time_str = input("Enter the time (HH:MM): ").strip()

    # Combine date and time into a single string
    datetime_str = f"{date_str} {time_str}"

    # Convert the combined string to epoch time
    try:
        time = arrow.get(datetime_str, 'YYYY-MM-DD HH:mm', tzinfo='Asia/Taipei').timestamp()
        time = int(time)
        # print(f"Converted date and time to epoch time: {time}")
    except arrow.parser.ParserError:
        print("Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
        sys.exit(1)
else:
    print("Invalid choice. Please enter 1 or 2.")
    sys.exit(1)

#Creating instances of the downloader and translators
downloader = ZendeskDownloader(email_address, api_token, time)

# Step 1: Choosing if you want to download ALL articles, or just articles after a specified time, to get the 
# list of all article IDs to download
if(time == 0):
    # OPTION 1: If you want to download all articles
    article_ids = downloader.list_all_articles()
else:
    # OPTION 2: If you want to download articles written/updated after a certain time,
    article_ids = downloader.list_articles()

# Step 2: Downloading articles from Zendesk
downloader.download_articles(article_ids)