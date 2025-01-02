import json, requests, os, arrow

class ZendeskDownloader:
    """
    A class to download articles from Zendesk Help Center incrementally based on their edited time.

    Attributes:
        subdomain (str): The Zendesk subdomain.
        user_email (str): The user's email address.
        api_token (str): The API token for authentication.
        end_time (int): The Unix timestamp to filter articles edited after this time.
    """
    def __init__(self, user_email, api_token, end_time):
        """
        Initializes the ZendeskDownloader with the given subdomain, user email, API token, and end time.

        Args:
            user_email (str): The user's email address.
            api_token (str): The API token for authentication.
            end_time (int): The Unix timestamp to filter articles edited after this time.
        """
        self.user_email = user_email
        self.api_token = api_token
        self.end_time = end_time
        self.start_time = self.end_time
        self.auth = f'{self.user_email}/token', self.api_token  # Authentication tuple for the API
        self.sections = []
        self.categories = []

    def list_all_articles(self):
        """
        Compiles a list of all the iD's of the existing articles uploaded

        Returns:
            [int]: List of all existing article iDs
        """
        
        url = f'https://studycat.zendesk.com/api/v2/help_center/articles.json?per_page=100&include=sections,section,categories'
        article_ids = []

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            self.sections = data['sections']
            self.categories = data['categories']
            for article in data['articles']:
                article_ids.append(article['id'])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")

        return article_ids

    def list_articles(self):
        """
        Lists articles that have been edited after the specified end_time.

        Returns:
            list: A list of article IDs that have been edited after the specified end_time.
        """
        # Base URL for the Zendesk API endpoint to retrieve incremental articles
        url = f'https://studycat.zendesk.com/api/v2/help_center/incremental/articles.json'
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

    # works for sections and categories
    def get_field_by_id(self, grouping, group_id, field):
        for group in grouping:
            if group['id'] == group_id:
                return group[field]
        return None

    def download_articles(self, article_ids):
        """
        Downloads the content of articles based on their IDs and saves them to a JSON file.

        Args:
            article_ids (list): A list of article IDs to download.

        Returns:
            list: A list of dictionaries containing article content.
        """
        articles = []
        for article_id in article_ids:
            # URL for retrieving individual article details
            url = f'https://studycat.zendesk.com/api/v2/help_center/articles/{article_id}.json'
            # Making the API request to get the article details
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                # Parsing the JSON response to get the article details
                article = response.json()['article']

                section_id = article['section_id']
                section_name = self.get_field_by_id(self.sections, section_id, 'name')

                category_id = self.get_field_by_id(self.sections, section_id, 'category_id')
                category_name = self.get_field_by_id(self.categories, category_id, 'name')

                # Creating a dictionary with the article's title, body, and ID
                article_content = {
                    'title': article['title'],
                    'body': article['body'],
                    'id': article['id'],
                    'section_id': section_id,
                    'section_name': section_name,
                    'category_id': category_id,
                    'category_name': category_name
                }
                if article['draft'] == False:
                # Adding the article content to the list
                    articles.append(article_content)
            else:
                # Log an error message if the API request failed
                print(f"Failed to download article {article_id}: {response.status_code}")
        print('about to save downloads)')

        # Saving the downloaded articles to a JSON file
        with open('articles_en.json', mode='w', encoding='utf-8') as f:
            json.dump(articles, f, sort_keys=True, indent=2)

        return articles
