from fetch_news import fetch_latest_news
from post_to_wordpress import post_to_wordpress
import requests

def main():
    news_articles = fetch_latest_news()
    for article in news_articles:
        title = article['title']
        content = f"{article['description']}<br>Read more: {article['url']}"
        image_url = article.get('urlToImage')
        try:
            post_to_wordpress(title, content, image_url)
            print(f"Posted: {title}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to post: {title}\nError: {e}")

if __name__ == "__main__":
    main()