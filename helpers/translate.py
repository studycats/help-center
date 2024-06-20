import json
from bs4 import BeautifulSoup
from googletrans import Translator

class ArticleTranslator:
    def __init__(self):
        self.translator = Translator()

    #Translating segments of text using the google translate API
    def translate_text(self, text, target_language):
        if text.strip():  # Ensure the text is not empty
            translated = self.translator.translate(text, dest=target_language)
            return translated.text
        return text  # Return the original text if empty

    def translate_html(self, html_content, target_language):
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup.find_all(string=True):
            if element.parent.name in ['h1', 'h2', 'h3', 'p', 'a', 'li']:
                try:
                    translated_text = self.translate_text(element.strip(), target_language)
                    element.replace_with(translated_text)
                except Exception as e:
                    # Minimize error messages, print only if critical
                    print(f"Could not translate: {element}, Error: {e}")
        return str(soup)

    def translate_article(self, article, target_language):
        try:
            translated_title = self.translate_text(article['title'], target_language)
            translated_body = self.translate_html(article['body'], target_language)
            
            translated_article = {
                'title': translated_title,
                'body': translated_body,
                'id': article['id']
            }
            return translated_article
        except Exception as e:
            print(f"Error translating article {article['id']}: {e}")
            return None

    def translate_articles(self, articles, target_language):
        translated_articles = []
        for article in articles:
            translated_article = self.translate_article(article, target_language)
            if translated_article:
                translated_articles.append(translated_article)
        return translated_articles
    
    def save_to_json(self, translated_articles, output_file, language_code):
        wrapped_content = {language_code: translated_articles}
        with open(output_file, mode='w', encoding='utf-8') as f:
            json.dump(wrapped_content, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    article_to_translate = {
    "body": "<h1><a href=\"https://studycat.com/product/fun-spanish/\" target=\"_self\">Fun Spanish</a></h1>\n<p>Like all our apps, Fun Spanish has been designed by teachers and language learning experts to inspire a passion for learning a new language.</p>\n<p>\u00a0</p>\n<table class=\" wysiwyg-text-align-center\" style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 15px; height: 179px; width: 520px;\">\n<tbody>\n<tr>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 250px;\">\n<h3 class=\"wysiwyg-text-align-center\"><strong>Limited Version<br><span class=\"wysiwyg-font-size-medium\">(Free)</span></strong></h3>\n</td>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 247px;\">\n<h3 class=\"wysiwyg-text-align-center\">Unlimited Version<br><span class=\"wysiwyg-font-size-medium\">(Paid - Subscription)</span>\n</h3>\n</td>\n</tr>\n<tr>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 250px;\">\n<ul>\n<li>2<span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>\u00a0themed courses</span>\n</li>\n<li><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>14 lessons</span></li>\n<li><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>30 words &amp; phrases</span></li>\n</ul>\n</td>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 247px;\">\n<ul>\n<li><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>12 themed courses</span></li>\n<li><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>70 lessons</span></li>\n<li>\n<span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>200 words &amp; phrases</span>\u00a0</li>\n</ul>\n</td>\n</tr>\n</tbody>\n</table>\n<p class=\"wysiwyg-text-align-left\">\u00a0</p>\n<p class=\"wysiwyg-text-align-left\"><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'>The<strong> Limited</strong> version is free and has limited access. Available themes are: <em>'Colours'</em> and <em>'Animals'.</em><br></span><span data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\" data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}'><br>The <strong>Unlimited</strong> version can be accessed by purchasing a monthly or annual subscription. You will have complete access to all available content.\u00a0</span></p>\n<p>\u00a0</p>",
    "id": 360051110994,
    "title": "Fun Spanish explained"
    }

    # Initialize translator
    translator = ArticleTranslator()

    # Translate article
    translated_article = translator.translate_article(article_to_translate, target_language='sv')

    if translated_article:
        # Output the translated article JSON
        print(json.dumps(translated_article, ensure_ascii=False, indent=2))
    else:
        print("Translation failed.")
