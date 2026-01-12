import feedparser
import trafilatura
import os

# CONFIGURATION
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"

def generate_smartnews_feed():
    d = feedparser.parse(ORIGINAL_FEED_URL)
    
    # Start building the XML string manually for better control
    articles_xml = ""
    
    for entry in d.entries[:20]:
        # Scrape full content
        downloaded = trafilatura.fetch_url(entry.link)
        full_content = trafilatura.extract(downloaded, output_format='html', include_tables=True, include_images=True)
        content_body = full_content if full_content else entry.summary

        articles_xml += f"""
        <item>
            <title>{entry.title}</title>
            <link>{entry.link}</link>
            <guid>{entry.link}</guid>
            <pubDate>{entry.published}</pubDate>
            <content:encoded><![CDATA[{content_body}]]></content:encoded>
        </item>"""

    # Combine into the full SmartFormat RSS structure
    full_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/" 
     xmlns:snf="http://www.smartnews.be/snf">
    <channel>
        <title>SatelliteInternet.com</title>
        <link>https://www.satelliteinternet.com</link>
        <description>SmartNews RSS Feed</description>
        <snf:logo><url>{LOGO_URL}</url></snf:logo>
        {articles_xml}
    </channel>
</rss>"""

    with open("smartnews.xml", "w", encoding="utf-8") as f:
        f.write(full_feed)

if __name__ == "__main__":
    generate_smartnews_feed()
