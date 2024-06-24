import json
from bs4 import BeautifulSoup
from googletrans import Translator
import re

class ArticleTranslator:
    def __init__(self):
        self.translator = Translator()
        self.phrases = ['Learn English', 'Learn Spanish', 'Learn German', 'Learn Chinese', 'Learn French']
        self.replacements = ['[EN]', '[ES]', '[DE]', '[ZH]', '[FR]']

    def substitution(self, text, list_originals, list_replacements):
        """
        Replaces phrases with placeholders before translation and vice versa after translation.

        Args:
            text (str): The text to perform substitution on.
            List_originals (list): The list of original phrases.
            List_replacements (list): The list of replacement placeholders.

        Returns:
            str: The text with phrases substituted.
        """
        for i in range(len(list_originals)):
            # Replace phrases, ignoring case
            replace = re.compile(re.escape(list_originals[i]), re.IGNORECASE)
            text = replace.sub(list_replacements[i], text)
        return text
    
    # NEW VERSION
    def translate_text(self, text, target_language):
        """
        Translates the given text to the target language, performing phrase substitution.

        Args:
            text (str): The text to translate.
            target_language (str): The target language code.

        Returns:
            str: The translated text.
        """
        if text.strip():  # Ensure the text is not empty
            # Substitute phrases with placeholders
            text = self.substitution(text, self.phrases, self.replacements)
            translated = self.translator.translate(text, dest=target_language)
            # Substitute placeholders back with original phrases
            translated_text = self.substitution(translated.text, self.replacements, self.phrases)
            return translated_text
        return text  # Return the original text if empty
    
    # #Translating segments of text using the google translate API
    # def translate_text(self, text, target_language):
    #     try:
    #         if text.strip():  # Ensure the text is not empty
    #             translated = self.translator.translate(text, dest=target_language)
    #             return translated.text
    #         return text  # Return the original text if empty
    #     except Exception as e:
    #                 print(f"Issue here: {text}, Error: {e.with_traceback}")
    #                 return text

    #OLD
    def translate_html(self, html_content, target_language):
        """
        Translates the text within an HTML content to the specified target language.

        Args:
            html_content (str): The HTML content to translate.
            target_language (str): The target language code.

        Returns:
            str: The translated HTML content.
        """
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Recursively translate text in HTML elements
        def translate_element(element):
            # If the element is a NavigableString (i.e., actual text), translate it
            if element.name is None:
                try:
                    translated_text = self.translate_text(element.strip(), target_language)
                    return translated_text
                except Exception as e:
                    print(f"Could not translate: {element}, Error: {e}")
                    return element

            # Otherwise, recursively translate the text of child elements
            for child in element.contents:
                translated_child = translate_element(child)
                if isinstance(translated_child, str):
                    child.replace_with(translated_child)
            return element

        # Start translation from the body of the HTML content
        translated_soup = translate_element(soup)

        # Return the translated HTML content as a string
        return str(translated_soup)

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
            print(f"Error translating article {e}")
            return None

    def translate_articles(self, articles, target_language):
        translated_articles = []
        for article in articles:
            translated_article = self.translate_article(article, target_language)
            if translated_article:
                translated_articles.append(translated_article)
        print("translated: ", translated_articles)
        return translated_articles
    
    def save_to_json(self, translated_articles, output_file, language_code):
        wrapped_content = {language_code: translated_articles}
        with open(output_file, mode='w', encoding='utf-8') as f:
            json.dump(wrapped_content, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__": 
    
    article_to_translate = {
    "body": "<h1 id=\"h_01J14B1TR93ZA0PMP07GX842GH\"><a href=\"https://studycat.com/product/fun-german/\" target=\"_self\">Learn German</a></h1>\n<p>From colours to food, animals to parts of the body, Learn German is designed to give your children an excellent base in the German language while having fun.</p>\n<p>\u00a0</p>\n<table class=\"wysiwyg-text-align-center\" style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 15px; height: 179px; width: 520px;\">\n<tbody>\n<tr>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 250px;\">\n<h3 id=\"h_01J14B1TR99N8CD8MVASM4X33S\" class=\"wysiwyg-text-align-center\">\n<strong>Limited Version<br></strong><span class=\"wysiwyg-font-size-medium\">(Free)</span>\n</h3>\n</td>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 247px;\">\n<h3 id=\"h_01J14B1TR9YSJ3QP3XF77ZDGBB\" class=\"wysiwyg-text-align-center\">Unlimited Version<br><span class=\"wysiwyg-font-size-medium\">(Paid - Subscription)</span>\n</h3>\n</td>\n</tr>\n<tr>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 250px;\">\n<ul>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">2 themed courses</span></li>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">13 lessons</span></li>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">30 words &amp; phrases</span></li>\n</ul>\n</td>\n<td class=\"wysiwyg-text-align-left\" style=\"width: 247px;\">\n<ul>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">10 themed courses</span></li>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">60 lessons</span></li>\n<li><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">155 words &amp; phrases</span></li>\n</ul>\n</td>\n</tr>\n</tbody>\n</table>\n<p class=\"wysiwyg-text-align-left\">\u00a0</p>\n<p class=\"wysiwyg-text-align-left\"><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\">The<strong> Limited</strong> version is free and has limited access. Available themes are: <em>'Colours' </em>and <em>'Animals'</em><em>.</em><br></span><span data-sheets-userformat='{\"2\":4482,\"4\":{\"1\":2,\"2\":16773836},\"10\":1,\"11\":4,\"15\":\"\\\"Courier New\\\"\"}' data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;\u2022 @free_lesson_count themed courses\\n\\n\u2022 @free_activity_count lessons\\n\\n\u2022 @free_song_count songs\\n\\n\u2022 Learn @free_vocab_total_count words &amp; phrases\\n\\nUpgrade to Unlimited\\nThe first 30 days are free. You won't be charged until the trial is over. Cancel anytime within the free trial period and pay nothing!&quot;}\"><br>The <strong>Unlimited</strong> version can be accessed by purchasing a monthly or annual subscription. You will have complete access to all available content.\u00a0</span></p>",
    "id": 360051872473,
    "title": "Learn German explained"
  }

    # Initialize translator
    translator = ArticleTranslator()

    # Translate article
    translated_article = translator.translate_article(article_to_translate, target_language='no')

    if translated_article:
        # Output the translated article JSON
        print(json.dumps(translated_article, ensure_ascii=False, indent=2))
    else:
        print("Translation failed.")
