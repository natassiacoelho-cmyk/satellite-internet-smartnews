import feedparser
import trafilatura
import re

# CONFIGURATION
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"
GA_ID = "G-4RNELPQG75"  # Your verified GA4 ID

def generate_smartnews_feed():
    d = feedparser.parse(ORIGINAL_FEED_URL)
    articles_xml = ""
    
    for entry in d.entries[:20]:
        try:
            downloaded = trafilatura.fetch_url(entry.link)
            full_content = trafilatura.extract(downloaded, output_format='html', include_tables=True, include_images=True)
            content_body = full_content if full_content else entry.summary
            
            # Find the first image for the thumbnail warning fix
            thumbnail_url = ""
            img_match = re.search(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', content_body)
            if img_match:
                thumbnail_url = img_match.group(1)
            
            media_tag = f'<media:thumbnail url="{thumbnail_url}" />' if thumbnail_url else ""

            # GA4 analytics tag for SmartNews SmartFormat
            analytics_tag = f"""<snf:analytics><![CDATA[
                <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
                <script>
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){{dataLayer.push(arguments);}}
                  gtag('js', new Date());
                  gtag('config', '{GA_ID}');
                </script>
            ]]></snf:analytics>"""

            content_body_safe = content_body.replace('&', '&amp;')

            articles_xml += f"""
        <item>
            <title>{entry.title}</title>
            <link>{entry.link}</link>
            <guid>{entry.link}</guid>
            <pubDate>{entry.published}</pubDate>
            <content:encoded><![CDATA[{content_body_safe}]]></content:encoded>
            {media_tag}
            {analytics_tag}
        </item>"""
        except Exception as e:
            print(f"Error on {entry.link}: {e}")

    full_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/" 
     xmlns:snf="http://www.smartnews.be/snf"
     xmlns:media="http://search.yahoo.com/mrss/">
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
