import json
import requests

class ZendeskDownloader:
    """This class gathers all the articles from the help centre, and downloads them
    as a JSON"""
    
    def __init__(self, subdomain):
        """Defining the domain of the zendesk website """

        self.subdomain = subdomain

    def list_articles(self):
        """Compiles a list of all the iD's of the existing articles uploaded

        Returns:
            [int]: List of all existing article iDs"""
        
        url = f'https://{self.subdomain}.zendesk.com/api/v2/help_center/articles.json'
        article_ids = []

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            for article in data['articles']:
                article_ids.append(article['id'])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")

        return article_ids

    def download_articles(self, article_ids):
        """Downloads articles corresponding to the article ID's input

        Args:
            article_ids ([int]): Article ID's of the articles to be downloaded

        Returns:
            JSon file: The downloaded articles, in a JSon file, which contains all HTML data 
            from the articles"""
        
        handoff_articles = []
        for article_id in article_ids:
            url = f'https://{self.subdomain}.zendesk.com/api/v2/help_center/articles/{article_id}.json'
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                article_content = {
                    'title': data['article']['title'],
                    'body': data['article']['body'],
                    'id': article_id
                }
                handoff_articles.append(article_content)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article {article_id}: {e}")
            except KeyError:
                print(f"Unexpected response structure for article {article_id}: {response.text}")

        with open('handoff_articles.json', mode='w', encoding='utf-8') as f:
            json.dump(handoff_articles, f, sort_keys=True, indent=2)

        return handoff_articles

if __name__ == "__main__":
    """Main class for the downloader, run this to download all articles"""

    # Defining our Zendesk subdomain
    subdomain = 'studycat'

    # Initialize ZendeskDownloader instance
    downloader = ZendeskDownloader(subdomain)

    # Step 1: Get the list of article IDs
    article_ids = downloader.list_articles()

    # Step 2: Download articles from Zendesk
    handoff_articles = downloader.download_articles(article_ids)
