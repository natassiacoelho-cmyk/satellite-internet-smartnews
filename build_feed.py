import feedparser
from trafilatura import fetch_url, extract
from feedgen.feed import FeedGenerator
import time

# Configuration
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://www.satelliteinternet.com/app/uploads/2026/01/satelliteinternet-logo_smartnews.webp"

def generate_smartnews_feed():
    # 1. Parse original feed
    d = feedparser.parse(ORIGINAL_FEED_URL)
    
    fg = FeedGenerator()
    fg.load_extension('content')
    # Add SmartNews Namespace
    fg.title('SatelliteInternet.com')
    fg.link(href='https://www.satelliteinternet.com', rel='alternate')
    fg.description('Satellite Internet Reviews and Guides')
    
    # 2. Process each article
    for entry in d.entries[:20]:  # Process last 20 articles
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.pubDate(entry.published)
        fe.guid(entry.link)
        
        # Scrape full text from the actual webpage
        downloaded = fetch_url(entry.link)
        full_content = extract(downloaded, include_tables=True, include_images=True)
        
        # Wrap in CDATA for SmartNews
        content_html = f"<![CDATA[ {full_content} ]]>"
        fe.content(content_html, type='html')

    # 3. Output the XML
    fg.rss_file('smartnews.xml', pretty=True)

if __name__ == "__main__":
    generate_smartnews_feed()
