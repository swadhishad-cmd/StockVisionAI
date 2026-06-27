import feedparser


def get_stock_news(company):

    url = f"https://news.google.com/rss/search?q={company}+stock"

    feed = feedparser.parse(url)

    news = []

    for entry in feed.entries[:5]:

        news.append({
            "title": entry.title,
            "link": entry.link
        })

    return news