import feedparser
from newspaper import Article
import csv
from datetime import datetime, timedelta, timezone
import requests
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; NewsScraper/1.0; +http://yourdomain.com)'
}

topics = {
    "immigration": {
        "conservative": {
            "Fox News Politics": "http://feeds.foxnews.com/foxnews/politics",
            "Fox News US Immigration": "https://www.foxnews.com/category/us/immigration/feed",
            "The Daily Caller": "https://dailycaller.com/feed/",
            "The Blaze": "https://www.theblaze.com/rss",
            "Breitbart": "http://feeds.feedburner.com/breitbart",
            "Breitbart Politics": "https://www.breitbart.com/politics/feed/",
            "National Review": "https://www.nationalreview.com/feed/",
            "The Washington Times": "https://www.washingtontimes.com/rss/feed/",
            "The Epoch Times": "https://www.theepochtimes.com/feed.xml",
            "Newsmax": "https://www.newsmax.com/rss/",
            "Townhall": "https://townhall.com/rss/rss.xml",
            "The Federalist": "https://thefederalist.com/feed/",
            "Daily Wire": "https://www.dailywire.com/rss",
            "One America News": "https://www.oann.com/feed/",
            "Washington Examiner": "https://www.washingtonexaminer.com/feed/rss",
            "American Thinker": "https://www.americanthinker.com/rss.xml",
            "The American Conservative": "https://www.theamericanconservative.com/feed/",
            "The Daily Signal": "https://www.dailysignal.com/feed/"
        },
        "moderate": {
            "Reuters": "https://www.reutersagency.com/feed/?best-topics=politics",
            "Associated Press Top News": "https://apnews.com/apf-topnews?format=rss",
            "Associated Press Politics": "https://apnews.com/apf-topnews?format=rss",
            "NPR General": "https://www.npr.org/rss/rss.php?id=1001",
            "NPR Politics": "https://www.npr.org/rss/rss.php?id=1014",
            "USA Today Nation": "https://rssfeeds.usatoday.com/UsatodaycomNation-TopStories",
            "USA Today Politics": "https://rssfeeds.usatoday.com/UsatodaycomPolitics-TopStories",
            "PBS NewsHour": "https://www.pbs.org/newshour/feed/",
            "PBS Newshour Politics": "https://www.pbs.org/newshour/politics/feed/",
            "Bloomberg Politics": "https://www.bloomberg.com/feed/podcast/politics.xml",
            "Politico": "https://www.politico.com/rss/politics08.xml",
            "The Hill": "https://thehill.com/rss/syndicator/19109",
            "CBS News Politics": "https://www.cbsnews.com/latest/rss/politics",
            "ABC News Politics": "https://abcnews.go.com/abcnews/politicsheadlines",
            "The Wall Street Journal General": "https://www.wsj.com/xml/rss/3_7014.xml",
            "The Wall Street Journal Politics": "https://www.wsj.com/xml/rss/3_7014.xml",
            "Financial Times": "https://www.ft.com/?format=rss",
            "The Christian Science Monitor": "https://www.csmonitor.com/feeds/rss",
            "Axios Politics": "https://www.axios.com/feed.xml",
            "BBC News US & Canada": "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
            "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml"
        },
        "liberal": {
            "CNN Politics": "http://rss.cnn.com/rss/edition_politics.rss",
            "CNN Immigration": "http://rss.cnn.com/rss/edition_us_immigration.rss",
            "The Guardian Immigration": "https://www.theguardian.com/us-news/immigration/rss",
            "Mother Jones": "https://www.motherjones.com/feed/",
            "MSNBC Latest": "http://www.msnbc.com/feeds/latest",
            "HuffPost Politics": "https://www.huffpost.com/section/politics/feed",
            "Vox": "https://www.vox.com/rss/index.xml",
            "Daily Kos": "https://www.dailykos.com/rss/main",
            "Salon": "https://www.salon.com/feed/",
            "The New Republic": "https://newrepublic.com/rss.xml",
            "The Atlantic": "https://www.theatlantic.com/feed/all/",
            "Slate": "https://slate.com/feed",
            "ThinkProgress (Archive)": "https://archive.thinkprogress.org/feed/",
            "The Nation": "https://www.thenation.com/feed/",
            "Common Dreams": "https://www.commondreams.org/feed/rss.xml",
            "Raw Story": "https://www.rawstory.com/rss/",
            "Truthout": "https://truthout.org/feed/",
            "Democracy Now": "https://www.democracynow.org/democracynow.rss"
        }
    }
}

MAX_ARTICLES_PER_IDEOLOGY = 3
MAX_ARTICLES_PER_OUTLET = 4

KEYWORDS = [
    "ice",
    "immigration and customs enforcement",
    "immigration enforcement",
    "deportation",
    "border patrol",
    "customs and border protection",
    "cbp",
    "detention center",
    "immigrant detention",
    "immigration raids",
    "immigration crackdown",
    "immigration policy",
    "immigration reform",
    "immigration laws",
    "immigration agents",
    "immigration officials",
    "border security",
    "migrant detention",
    "immigration detention facility",
    "immigration court",
    "immigrant rights",
    "family separation",
    "sanctuary cities",
    "deportee",
    "ice agents",
    "undocumented immigrants",
    "migrant caravan",
    "asylum seekers",
    "border crossing",
    "illegal immigration",
    "immigration ban",
    "visa policy",
    "naturalization",
    "immigration detention center",
    "immigration raid",
    "deportee",
    "migration policy",
    "refugee status",
    "immigration",
    "border",
    "border security",
    "asylum",
    "visa",
    "green card",
    "immigration reform",
    "deportation",
    "ICE",
    "CBP",
    "citizenship",
    "migrant policy",
    "migrant caravan",
    "border wall",
    "refugee",
    "work permit",
    "naturalization",
    "detention center",
    "family separation",
    "Title 42",
    "parole program",
    "illegal immigration",
    "mass migration",
    "undocumented immigrants",
    "sanctuary city",
    "sanctuary cities",
    "amnesty",
    "open borders",
    "migrant surge",
    "immigration",
    "border",
    "border security",
    "asylum",
    "visa",
    "green card",
    "immigration reform",
    "deportation",
    "ICE",
    "CBP",
    "citizenship",
    "migrant policy",
    "migrant caravan",
    "border wall",
    "refugee",
    "work permit",
    "naturalization",
    "detention center",
    "family separation",
    "Title 42",
    "parole program",
    "illegal immigration",
    "mass migration",
    "undocumented immigrants",
    "sanctuary city",
    "sanctuary cities",
    "amnesty",
    "open borders",
    "migrant surge",
    "border patrol",
    "immigration raid",
    "ICE raid",
    "removal proceedings",
    "immigration detention",
    "immigration enforcement",
    "immigration crackdown",
    "expedited removal",
    "temporary protected status",
    "TPS",
    "DACA",
    "Dreamers",
    "E-Verify",
    "immigration court",
    "customs enforcement",
    "ICE facility",
    "immigration prison",
    "deferred action",
    "catch and release",
    "migrant processing",
    "detention facility",
    "ICE detention",

]

KEYWORDS = [k.lower() for k in KEYWORDS]

def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5, headers=HEADERS)
        if response.status_code == 200:
            return True
        response = requests.get(url, stream=True, timeout=5, headers=HEADERS)
        return response.status_code == 200
    except requests.RequestException:
        return False

def to_naive(dt):
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def is_recent(publish_date, days=30):
    publish_date_naive = to_naive(publish_date)
    now_naive = datetime.utcnow()
    if not publish_date_naive:
        return False
    return publish_date_naive >= now_naive - timedelta(days=days)

def contains_keyword_in_title(title, keywords):
    title = title.lower()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, title):
            return True
    return False

output_rows = []
topic = "immigration"
ideologies = topics[topic]

counts = {ideo: 0 for ideo in ideologies}
outlet_counts = {ideo: {outlet: 0 for outlet in outlets} for ideo, outlets in ideologies.items()}

print(f"Starting scraping articles on '{topic}' topic...")

# Loop until each ideology reaches max article count
while any(counts[ideo] < MAX_ARTICLES_PER_IDEOLOGY for ideo in counts):
    for ideology, outlets in ideologies.items():
        if counts[ideology] >= MAX_ARTICLES_PER_IDEOLOGY:
            continue

        for outlet, feed_url in outlets.items():
            if outlet_counts[ideology][outlet] >= MAX_ARTICLES_PER_OUTLET:
                continue

            print(f"Fetching feed: {outlet} ({ideology})")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if counts[ideology] >= MAX_ARTICLES_PER_IDEOLOGY or outlet_counts[ideology][outlet] >= MAX_ARTICLES_PER_OUTLET:
                    break

                url = entry.link
                if not url_exists(url):
                    continue

                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                except Exception:
                    continue

                # Get publish date
                publish_date = None
                if hasattr(article, 'publish_date') and article.publish_date:
                    publish_date = article.publish_date
                elif hasattr(entry, 'published_parsed'):
                    publish_date = datetime(*entry.published_parsed[:6])

                if not is_recent(publish_date):
                    continue

                title = article.title if article and article.title else (entry.title if hasattr(entry, 'title') else "")
                sample_text = article.text[:10000].strip() if article and article.text else ""

                if not sample_text:
                    continue

                # STRICT keyword check only in title (whole word matching)
                if not contains_keyword_in_title(title, KEYWORDS):
                    continue

                # Skip duplicates
                if any(row["url"] == url for row in output_rows):
                    continue

                datetime_str = publish_date.strftime("%Y-%m-%d %H:%M") if publish_date else ""

                output_rows.append({
                    "topic": topic,
                    "outlet": outlet,
                    "datetime": datetime_str,
                    "title": title,
                    "url": url,
                    "sample_text": sample_text,
                    "ideological_stance": ideology,
                    "factual_grounding": "",
                    "framing_choices": "",
                    "emotional_tone": "",
                    "source_transparency": ""
                })

                counts[ideology] += 1
                outlet_counts[ideology][outlet] += 1

                print(f"Added article ({counts[ideology]}/{MAX_ARTICLES_PER_IDEOLOGY}) from {outlet} ({ideology})")

            if counts[ideology] >= MAX_ARTICLES_PER_IDEOLOGY:
                print(f"Reached max articles for {ideology}")

print("Scraping done. Saving to CSV...")

csv_columns = [
    "topic", "outlet", "datetime", "title", "url", "sample_text",
    "ideological_stance", "factual_grounding", "framing_choices", "emotional_tone", "source_transparency"
]

with open("news_bias_articles.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    writer.writerows(output_rows)

print("Done! Articles saved to news_bias_articles.csv")

