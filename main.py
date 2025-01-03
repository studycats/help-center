import sys, arrow
from download import download_articles

# Headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


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

download_articles(time)