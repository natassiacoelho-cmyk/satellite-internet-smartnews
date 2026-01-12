import feedparser
import trafilatura
import os

# CONFIGURATION
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"

def generate_smartnews_feed():
    # 1. Parse the original snippet-only feed
    d = feedparser.parse(ORIGINAL_FEED_URL)
    articles_xml = ""
    
    # 2. Process up to 20 entries
    for entry in d.entries[:20]:
        try:
            # Fetch the full page with a browser-like signature
            downloaded = trafilatura.fetch_url(entry.link, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Extract content as HTML with high precision settings
            # This ensures we get the body, tables, and images without sidebars
            full_content = trafilatura.extract(
                downloaded, 
                output_format='html', 
                include_tables=True, 
                include_images=True,
                include_links=True,
                favor_precision=True
            )
            
            # Use scraped content, or fallback to the summary if scraping fails
            content_body = full_content if full_content else entry.summary
            
            # Clean only the Ampersand to keep the XML valid while preserving HTML tags
            content_body = content_body.replace('&', '&amp;')

            # Build the individual article item
            articles_xml += f"""
        <item>
            <title>{entry.title}</title>
            <link>{entry.link}</link>
            <guid>{entry.link}</guid>
            <pubDate>{entry.published}</pubDate>
            <content:encoded><![CDATA[{content_body}]]></content:encoded>
        </item>"""
        except Exception as e:
            print(f"Skipping article {entry.link} due to error: {e}")

    # 3. Assemble the full SmartFormat RSS structure
    full_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:snf="http://www.smartnews.be/snf">
    <channel>
        <title>SatelliteInternet.com</title>
        <link>https://www.satelliteinternet.com</link>
        <description>SmartNews RSS Feed</description>
        <snf:logo><url>{LOGO_URL}</url></snf:logo>
        {articles_xml}
    </channel>
</rss>"""

    # 4. Save the file with UTF-8 encoding to handle special characters
    with open("smartnews.xml", "w", encoding="utf-8") as f:
        f.write(full_feed)

if __name__ == "__main__":
    generate_smartnews_feed()
