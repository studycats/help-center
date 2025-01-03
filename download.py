# Downloads articles from Zendesk Help Center incrementally based on their edited time.
import json, requests, arrow, os
from dotenv import load_dotenv

load_dotenv

email_address = os.getenv("ZENDESK_EMAIL_ADDRESS")
api_token = os.getenv("ZENDESK_API_TOKEN")

# Combine email and API token for basic authentication
auth = (f'{email_address}/token', api_token)

# Lists articles that have been edited after the specified time.
def list_articles(time):
    if time == 0:
        url = 'https://studycat.zendesk.com/api/v2/help_center/articles.json?per_page=100&include=sections,section,categories'
    else:
        url = f'https://studycat.zendesk.com/api/v2/help_center/incremental/articles.json?start_time={time}&per_page=100&include=sections,section,categories'

    article_ids = []
    
    try:
        if time == 0:
            response = requests.get(url)
        else:
            response = requests.get(url, auth=auth)

        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        sections = data['sections']
        categories = data['categories']
        for article in data['articles']:
            article_ids.append(article['id'])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")

    return article_ids, sections, categories

# works for sections and categories
def get_field_by_id(grouping, group_id, field):
    for group in grouping:
        if group['id'] == group_id:
            return group[field]
    return None

def download_articles(time):
    """
    Downloads the content of articles based on their IDs and saves them to a JSON file.

    Args:
        article_ids (list): A list of article IDs to download.

    Returns:
        list: A list of dictionaries containing article content.
    """
    article_ids, sections, categories = list_articles(time)

    articles = []
    for article_id in article_ids:
        # URL for retrieving individual article details
        url = f'https://studycat.zendesk.com/api/v2/help_center/articles/{article_id}.json'
        # Making the API request to get the article details
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            # Parsing the JSON response to get the article details
            article = response.json()['article']

            section_id = article['section_id']
            section_name = get_field_by_id(sections, section_id, 'name')

            category_id = get_field_by_id(sections, section_id, 'category_id')
            category_name = get_field_by_id(categories, category_id, 'name')

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
            if not article['draft']:
            # Adding the article content to the list
                articles.append(article_content)
        else:
            # Log an error message if the API request failed
            print(f"Failed to download article {article_id}: {response.status_code}")

    # Saving the downloaded articles to a JSON file
    with open('articles_en.json', mode='w', encoding='utf-8') as f:
        json.dump(articles, f, sort_keys=True, indent=2)

    return articles
