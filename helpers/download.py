import json
import requests
import os
import arrow

class ZendeskDownloader:
    """
    A class to download articles from Zendesk Help Center incrementally based on their edited time.

    Attributes:
        subdomain (str): The Zendesk subdomain.
        user_email (str): The user's email address.
        api_token (str): The API token for authentication.
        end_time (int): The Unix timestamp to filter articles edited after this time.
    """
    def __init__(self, subdomain, user_email, api_token, end_time):
        """
        Initializes the ZendeskDownloader with the given subdomain, user email, API token, and end time.

        Args:
            subdomain (str): The Zendesk subdomain.
            user_email (str): The user's email address.
            api_token (str): The API token for authentication.
            end_time (int): The Unix timestamp to filter articles edited after this time.
        """
        self.subdomain = subdomain
        self.user_email = user_email
        self.api_token = api_token
        self.end_time = end_time
        self.start_time = self.end_time
        self.auth = f'{self.user_email}/token', self.api_token  # Authentication tuple for the API

    def list_all_articles(self):
        """
        Compiles a list of all the iD's of the existing articles uploaded

        Returns:
            [int]: List of all existing article iDs
        """
        
        url = f'https://{self.subdomain}.zendesk.com/api/v2/help_center/articles.json?per_page=100'
        article_ids = []

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            for article in data['articles']:
                article_ids.append(article['id'])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")

        # Excluding the "Learn X explained" articles, these have special formatting and must be manually changed
        excluded_ids = [360051111134, 360050856654, 4411938668441, 360051872473, 360051110994]

        for id in excluded_ids:
            if id in article_ids:
                article_ids.remove(id)

        return article_ids

    def list_articles(self):
        """
        Lists articles that have been edited after the specified end_time.

        Returns:
            list: A list of article IDs that have been edited after the specified end_time.
        """
        # Base URL for the Zendesk API endpoint to retrieve incremental articles
        url = f'https://{self.subdomain}.zendesk.com/api/v2/help_center/incremental/articles.json'
        article_ids = []

        while url:
            # Parameters for the API request, starting with the last known timestamp
            params = {'start_time': self.start_time}
            # Making the API request with the URL, parameters, and authentication
            response = requests.get(url, params=params, auth=self.auth)
            if response.status_code == 200:
                # Parsing the JSON response
                data = response.json()
                for article in data['articles']:
                    # Logging each article's information and edit timestamp
                    print("article: ", article, " edited at: ", arrow.get(article['edited_at']).timestamp())
                    # If the article was edited after the end_time, continue to the next article
                    # Also, ensuring the articles are downloaded from the English version only
                    if article['locale'] == 'en-us' and arrow.get(article['edited_at']).timestamp() > self.end_time:
                        # Adding the article ID to the list if it meets the criteria
                        article_ids.append(article['id'])
                
                # Check if there's a next page of results and update the URL
                if data['next_page']:
                    self.start_time = data['end_time']  # Update start_time for the next request
                    url = data['next_page']  # Update the URL to the next page
                else:
                    # No more pages, update end_time and stop the loop
                    self.end_time = data['end_time']
                    url = None
            else:
                # Log an error message if the API request failed
                print(f"Failed to retrieve articles: {response.status_code}")
                url = None
         # Print the end_time to be used in the next export
        print(f'- use the following end time value in the next export: {self.end_time}')
        return article_ids

    def download_articles(self, article_ids):
        """
        Downloads the content of articles based on their IDs and saves them to a JSON file.

        Args:
            article_ids (list): A list of article IDs to download.

        Returns:
            list: A list of dictionaries containing article content.
        """
        handoff_articles = []
        for article_id in article_ids:
            # URL for retrieving individual article details
            url = f'https://{self.subdomain}.zendesk.com/api/v2/help_center/articles/{article_id}.json'
            # Making the API request to get the article details
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                # Parsing the JSON response to get the article details
                article = response.json()['article']
                # Creating a dictionary with the article's title, body, and ID
                article_content = {
                    'title': article['title'],
                    'body': article['body'],
                    'id': article['id']
                }
                if article['draft'] == False:
                # Adding the article content to the list
                    handoff_articles.append(article_content)
            else:
                # Log an error message if the API request failed
                print(f"Failed to download article {article_id}: {response.status_code}")

        # Saving the downloaded articles to a JSON file
        with open('handoff_articles.json', mode='w', encoding='utf-8') as f:
            json.dump(handoff_articles, f, sort_keys=True, indent=2)

        return handoff_articles
    
if __name__ == "__main__":
    """Main class for the downloader, run this to download all articles"""

    # Defining our Zendesk subdomain
    subdomain = 'studycat'

    # Initialize ZendeskDownloader instance
    downloader = ZendeskDownloader(subdomain, os.getenv("ZENDESK_EMAIL_ADDRESS"), os.getenv("ZENDESK_API_TOKEN"), 1719197940)

    # Step 1: Get the list of article IDs
    article_ids = downloader.list_all_articles()

    # Step 2: Download articles from Zendesk
    handoff_articles = downloader.download_articles(article_ids)


    