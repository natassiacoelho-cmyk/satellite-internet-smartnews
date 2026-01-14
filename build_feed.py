import feedparser
import trafilatura
import re
import requests

# CONFIGURATION
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"
GA_ID = "G-4RNELPQG75" 

def generate_smartnews_feed():
    d = feedparser.parse(ORIGINAL_FEED_URL)
    articles_xml = ""
    
    if not d.entries:
        return

    for entry in d.entries[:20]:
        try:
            # 1. Fetch HTML with a browser-like signature
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(entry.link, headers=headers, timeout=15)
            html_doc = response.text

            # 2. Scrape with Fallback logic
            full_content = trafilatura.extract(html_doc, output_format='html', include_tables=True, include_images=True, favor_recall=True)
            
            # THE SAFETY NET: Use full content if found, otherwise use original summary
            content_body = full_content if (full_content and len(full_content) > 200) else entry.summary
            
            # Clean technical junk
            content_body = re.sub(r'data-widget="[^"]+"', '', content_body)
            content_body = re.sub(r'class="[^"]+"', '', content_body)

            # 3. Find Thumbnail
            thumbnail_url = ""
            og_image = re.search(r'property="og:image" content="([^"]+)"', html_doc)
            if og_image:
                thumbnail_url = og_image.group(1)
            media_tag = f'<media:thumbnail url="{thumbnail_url}" />' if thumbnail_url else ""

            # 4. Single-Script GA4 Analytics
            analytics_tag = f"""<snf:analytics><![CDATA[
                <script>
                  (function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
                  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
                  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                  'https://www.googletagmanager.com/gtag/js?id='+i+dl;f.parentNode.insertBefore(j,f);
                  }})(window,document,'script','dataLayer','{GA_ID}');
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
