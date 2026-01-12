import feedparser
import trafilatura
from feedgen.feed import FeedGenerator

# CONFIGURATION
# Use the Raw GitHub URL for your logo to avoid the WordPress .webp issue
ORIGINAL_FEED_URL = "https://www.satelliteinternet.com/feed"
LOGO_URL = "https://raw.githubusercontent.com/natassiacoelho-cmyk/satellite-internet-smartnews/main/satelliteinternet-logo_smartnews.png"

def generate_smartnews_feed():
    d = feedparser.parse(ORIGINAL_FEED_URL)
    
    fg = FeedGenerator()
    # Load the SmartNews extension
    fg.load_extension('snf', atom=False, rss=True)
    
    fg.title('SatelliteInternet.com')
    fg.link(href='https://www.satelliteinternet.com', rel='alternate')
    fg.description('Your guide to satellite internet providers and news.')
    
    # Set the logo using the specific SmartNews tag
    fg.snf.logo(LOGO_URL)

    for entry in d.entries[:20]:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.guid(entry.link)
        fe.pubDate(entry.published)
        
        # Pull full content to bypass WordPress snippet limitation
        downloaded = trafilatura.fetch_url(entry.link)
        full_content = trafilatura.extract(downloaded, output_format='html', include_tables=True, include_images=True)
        
        if full_content:
            # Wrap in CDATA to ensure validation
            fe.content(f"<![CDATA[{full_content}]]>", type='html')
        else:
            fe.content(f"<![CDATA[{entry.summary}]]>", type='html')

    fg.rss_file('smartnews.xml', pretty=True)

if __name__ == "__main__":
    generate_smartnews_feed()
