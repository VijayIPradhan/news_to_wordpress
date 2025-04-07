import requests
from config import NEWS_API_KEY, NEWS_API_URL

def fetch_latest_news():
    params = {
        'apiKey': NEWS_API_KEY,
        'category': 'general',
        'pageSize': 10
    }
    response = requests.get(NEWS_API_URL, params=params)
    response.raise_for_status()
    news_data = response.json()
    return news_data['articles']