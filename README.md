# Zendesk Article Translator and Uploader

This project provides tools for downloading articles from a Zendesk help center, translating them into multiple languages, and uploading the translated articles back to Zendesk.

**Authors: Christian Borup :see_no_evil:, Malin Leven :stuck_out_tongue_winking_eye: (Podsters Summer 2024)** <br />
Recently updated: 04/07/2024

## Classes Overview

### `ZendeskDownloader`

- **Purpose**: Gathers all the articles from the help center and downloads them as JSON files.

### `Main`

- **Purpose**: Combines the downloading, translating, and uploading process into one. Running this script completes all the tasks above.

## How to run

1. Clone the repository
2. Open project (preferably using VSCode)
3. Create .env file (see below)
4. Navigate to the main class, run

**IMPORTANT: In order to ensure security, the Zendesk e-mail and API key have been hidden in an env file.** <br />
_In order to run this program, you must create your own .env file in the main directory, then add your authorized
Zendesk email address and API Key:_

ZENDESK_EMAIL_ADDRESS={username@email.com}<br />
ZENDESK_API_TOKEN={your-key}

## Dependencies

- requests
- beautifulsoup4
- googletrans
- python-dotenv

## Acknowledgements

- BeautifulSoup
- Google Translate API
- Zendesk API
