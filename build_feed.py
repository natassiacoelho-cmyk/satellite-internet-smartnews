import feedparser
import trafilatura
import re

# CONFIGURATION
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"

# TODO: Replace 'UA-XXXXXXXXX-X' with your actual Google Analytics ID if you have one
GA_ID = "UA-XXXXXXXXX-X" 

def generate_smartnews_feed():
    d = feedparser.parse(ORIGINAL_FEED_URL)
    articles_xml = ""
    
    for entry in d.entries[:20]:
        try:
            downloaded = trafilatura.fetch_url(entry.link)
            full_content = trafilatura.extract(downloaded, output_format='html', include_tables=True, include_images=True)
            content_body = full_content if full_content else entry.summary
            
            # 1. Try to find the first image URL to use as a thumbnail
            thumbnail_url = ""
            img_match = re.search(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', content_body)
            if img_match:
                thumbnail_url = img_match.group(1)
            
            # Build the thumbnail tag if an image was found
            media_tag = f'<media:thumbnail url="{thumbnail_url}" />' if thumbnail_url else ""

            # 2. Add Analytics tracking (placeholder)
            analytics_tag = f"""<snf:analytics><![CDATA[
                <script>
                  (function(i,s,o,g,r,a,m){{i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){{
                  (i[r].q=i[r].q||[]).push(arguments)}},i[r].l=1*new Date();a=s.createElement(o),
                  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                  }})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
                  ga('create', '{GA_ID}', 'auto');
                  ga('send', 'pageview');
                </script>
            ]]></snf:analytics>"""

            # Clean ampersands for XML
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
