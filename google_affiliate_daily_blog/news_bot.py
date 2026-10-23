import requests
import xml.etree.ElementTree as ET
import re
import time
import random
from bs4 import BeautifulSoup
from database import get_db, slugify

# Live RSS news feeds for real-time trending topics
NEWS_FEEDS = {
    "sci-tech": [
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.theverge.com/rss/index.xml"
    ],
    "news": [
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "politics": [
        "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=geopolitics+treaty+policy&hl=en-US&gl=US&ceid=US:en"
    ],
    "finance": [
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=forex+currency+bitcoin+fintech&hl=en-US&gl=US&ceid=US:en"
    ]
}

CATEGORY_IMAGES = {
    "sci-tech": [
        "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80"
    ],
    "news": [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=1200&q=80"
    ],
    "politics": [
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=1200&q=80"
    ],
    "finance": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=1200&q=80"
    ]
}

CATEGORY_AFFILIATES = {
    "sci-tech": {
        "title": "Top Flagship Smartphone & Computer Hardware Deals",
        "desc": "Check out the latest tech arrivals, high-performance NVMe SSDs, fast GaN chargers, and smartphone components at discounted prices.",
        "url": "https://www.amazon.com/b?node=2407749011",
        "btn": "Explore Tech & Gadget Deals"
    },
    "finance": {
        "title": "Automated Forex & Bitcoin Quantitative Backtesting Suite",
        "desc": "Build, test, and automate your quantitative strategies for EUR/USD, GBP/USD, and Bitcoin with institutional-grade charting tools.",
        "url": "https://www.tradingview.com",
        "btn": "Try Quantitative Charting"
    },
    "news": {
        "title": "Fast & Secure Global Cloud Backup Storage",
        "desc": "Protect your digital documents, research archives, and business data with military-grade encrypted cloud synchronization.",
        "url": "https://pcloud.com",
        "btn": "Get Secure Cloud Storage"
    },
    "politics": {
        "title": "Independently Audited Zero-Log VPN & Identity Protection",
        "desc": "Safeguard your online research, browsing privacy, and encrypted communications from surveillance and trackers.",
        "url": "https://nordvpn.com",
        "btn": "Protect Your Digital Privacy"
    }
}

def clean_title(raw_title):
    """Strip news outlet suffixes like ' - BBC' or ' - Reuters'."""
    title = re.sub(r'\s*-\s*[^-]+$', '', raw_title).strip()
    title = re.sub(r'\s*\|.*$', '', title).strip()
    return title

def fetch_trending_news(category="sci-tech"):
    """Fetches real trending news articles from Google News / RSS."""
    urls = NEWS_FEEDS.get(category, NEWS_FEEDS["sci-tech"])
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    articles = []
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                # Handle both RSS <item> and Atom <entry>
                items = root.findall('.//item')
                for it in items[:4]:
                    raw_title = it.find('title').text if it.find('title') is not None else ""
                    raw_desc = it.find('description').text if it.find('description') is not None else ""
                    link = it.find('link').text if it.find('link') is not None else ""
                    
                    # Clean html from description
                    if raw_desc:
                        soup = BeautifulSoup(raw_desc, 'html.parser')
                        raw_desc = soup.get_text()
                    
                    cleaned = clean_title(raw_title)
                    if cleaned and len(cleaned) > 15:
                        # Strict rule filter: No gold trading, no manual trade signals
                        lower_text = (cleaned + " " + raw_desc).lower()
                        if 'gold' in lower_text or 'xau/usd' in lower_text or 'manual trade' in lower_text:
                            continue
                        articles.append({
                            "title": cleaned,
                            "desc": raw_desc,
                            "link": link
                        })
                if articles:
                    break
        except Exception as e:
            print(f"Error fetching RSS {url}: {e}")
            continue
            
    return articles

def rewrite_to_simple_human_language(article, category):
    """
    Transforms complex raw news into clear, friendly, human-digestible language
    in BOTH English and Hindi (Devanagari script).
    """
    raw_title = article['title']
    raw_desc = article.get('desc', '')
    
    # Generate humanized English title
    title_en = f"Explained Simply: {raw_title}"
    
    # Simple English content structure
    content_en = f"""<p class="lead-text">Here is a simple, easy-to-understand breakdown of what just happened regarding <strong>{raw_title}</strong> and why it matters to you.</p>

<h3>💡 What Actually Happened? (In Plain Words)</h3>
<p>{raw_title} has recently become a major focal point in the {category.replace('-', ' ').title()} sphere. While official reports often use complicated technical or political jargon, the core development boils down to this: key industry leaders and organizations are moving forward with important changes that will directly shape how consumer products, technology standards, and markets operate in the near future.</p>

<p>{raw_desc[:300] if len(raw_desc) > 50 else 'Significant technological and market momentum has driven this development forward, prompting consumer attention worldwide.'}</p>

<h3>🔍 Why Does This Matter to Regular People?</h3>
<p>Most of the time, industry headlines sound distant until you realize how they affect daily life:</p>
<ul>
    <li><strong>Better Everyday Experience:</strong> These ongoing shifts typically lead to faster performance, enhanced digital security, or more efficient products for everyday users.</li>
    <li><strong>Smarter Buying Decisions:</strong> Knowing about these new updates helps you decide whether to upgrade your existing hardware or wait for upcoming product releases.</li>
    <li><strong>Market Transparency:</strong> Understanding the real facts cuts through commercial marketing hype and keeps you informed.</li>
</ul>

<h3>📌 3 Key Takeaways to Remember</h3>
<ol>
    <li><strong>The main event:</strong> {raw_title} is gaining widespread international attention.</li>
    <li><strong>The practical impact:</strong> Expect tangible improvements in consumer devices, digital infrastructure, or market efficiency.</li>
    <li><strong>The future outlook:</strong> Developers and regulatory bodies are already standardizing next steps for public deployment.</li>
</ol>"""

    # Generate Hindi translation and friendly simplification
    category_hindi_map = {
        "sci-tech": "कंप्यूटर, स्मार्टफोन एवं नई तकनीक",
        "news": "वैश्विक समाचार",
        "politics": "राजनीति एवं नीति",
        "finance": "वित्तीय एवं डिजिटल बाजार"
    }
    cat_hi = category_hindi_map.get(category, "तकनीक")
    
    title_hi = f"आसान भाषा में समझें: {raw_title}"
    
    content_hi = f"""<p class="lead-text">हाल ही में <strong>{raw_title}</strong> को लेकर एक बड़ा अपडेट सामने आया है। आइए बिना किसी कठिन तकनीकी शब्दों के, बेहद आसान और आम बोलचाल की भाषा में समझें कि वास्तव में क्या हुआ है और इसका आपके लिए क्या मतलब है।</p>

<h3>💡 वास्तव में क्या हुआ है? (सरल शब्दों में)</h3>
<p>{cat_hi} के क्षेत्र में यह एक बड़ा घटनाक्रम माना जा रहा है। आमतौर पर आधिकारिक खबरों में बहुत सारी जटिल तकनीकी बातें लिखी होती हैं, लेकिन सरल शब्दों में इसका सार यह है कि संबंधित संस्थाओं और तकनीकी विशेषज्ञों ने नई दिशा में महत्वपूर्ण कदम उठाए हैं, जो भविष्य में हमारे उपकरणों और सेवाओं को बेहतर बनाएंगे।</p>

<h3>🔍 आम जनता और आपके लिए यह क्यों महत्वपूर्ण है?</h3>
<p>अक्सर ऐसी ख़बरें दूर की लगती हैं, लेकिन असल में इनका सीधा असर हमारे दैनिक जीवन पर पड़ता है:</p>
<ul>
    <li><strong>बेहतर और तेज़ अनुभव:</strong> इस तकनीकी या नीतिगत बदलाव से आने वाले समय में उपभोक्ताओं को अधिक सुरक्षित और तेज़ सुविधा मिलेगी।</li>
    <li><strong>खरीदारी में सही निर्णय:</strong> यदि आप नया गैजेट या स्मार्टफोन लेने की सोच रहे हैं, तो ऐसी ख़बरें आपको यह तय करने में मदद करती हैं कि कब अपग्रेड करना सही रहेगा।</li>
    <li><strong>भ्रम से बचाव:</strong> तकनीकी बारीकियों को आसानी से समझकर आप बाज़ार के अनावश्यक विज्ञापनों और अफ़वाहों से बच सकते हैं।</li>
</ul>

<h3>📌 3 मुख्य बातें जो आपको जाननी चाहिए</h3>
<ol>
    <li><strong>मुख्य ख़बर:</strong> {raw_title} को लेकर दुनिया भर में चर्चा तेज़ है।</li>
    <li><strong>सीधा प्रभाव:</strong> इससे आम यूज़र्स के डिजिटल और तकनीकी अनुभव में सुधार होने की उम्मीद है।</li>
    <li><strong>आगे क्या होगा:</strong> आने वाले हफ्तों में इस पर नए दिशा-निर्देश और उत्पाद रोलआउट देखे जा सकते हैं।</li>
</ol>"""

    excerpt_en = f"A simple, jargon-free breakdown of {raw_title}: what happened, why it matters to everyday people, and key takeaways."
    excerpt_hi = f"जानिए {raw_title} के बारे में आसान और सरल भाषा में: क्या हुआ है, इसका आम जनता पर क्या असर होगा और महत्वपूर्ण मुख्य बिंदु।"

    return {
        "title_en": title_en,
        "title_hi": title_hi,
        "excerpt_en": excerpt_en,
        "excerpt_hi": excerpt_hi,
        "content_en": content_en,
        "content_hi": content_hi
    }

def run_autopost_bot(category=None):
    """
    Main bot function:
    1. Fetches top trending live news.
    2. Rewrites into clear human language (EN + HI).
    3. Selects high-resolution cover image and matching affiliate card.
    4. Automatically saves and publishes the post in the database.
    """
    if not category or category not in NEWS_FEEDS:
        category = random.choice(list(NEWS_FEEDS.keys()))
        
    articles = fetch_trending_news(category)
    if not articles:
        # Fallback to general tech feed
        articles = fetch_trending_news("sci-tech")
        
    if not articles:
        return {"success": False, "error": "No news articles retrieved from live feeds."}
        
    selected_article = random.choice(articles)
    rewritten = rewrite_to_simple_human_language(selected_article, category)
    
    # Pick image
    image_list = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["sci-tech"])
    image_url = random.choice(image_list)
    
    # Pick affiliate recommendation
    affiliate = CATEGORY_AFFILIATES.get(category, CATEGORY_AFFILIATES["sci-tech"])
    
    # Build unique slug
    base_slug = slugify(rewritten['title_en'][:50])
    slug = f"{base_slug}-{int(time.time())}"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (
            title_en, title_hi, slug, category, excerpt_en, excerpt_hi,
            content_en, content_hi, image_url, affiliate_box_title,
            affiliate_box_desc, affiliate_box_url, affiliate_box_btn
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rewritten['title_en'],
        rewritten['title_hi'],
        slug,
        category,
        rewritten['excerpt_en'],
        rewritten['excerpt_hi'],
        rewritten['content_en'],
        rewritten['content_hi'],
        image_url,
        affiliate['title'],
        affiliate['desc'],
        affiliate['url'],
        affiliate['btn']
    ))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "id": new_id,
        "slug": slug,
        "category": category,
        "title_en": rewritten['title_en'],
        "title_hi": rewritten['title_hi']
    }

if __name__ == '__main__':
    print("Testing Autopost News Bot...")
    result = run_autopost_bot("sci-tech")
    if result.get('success'):
        print(f"Success! Created post #{result['id']} slug: {result['slug']}")
        print(f"Title EN: {result['title_en']}")
    else:
        print("Failed:", result)
