import sqlite3
import os
import re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_en TEXT NOT NULL,
            title_hi TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            excerpt_en TEXT,
            excerpt_hi TEXT,
            content_en TEXT NOT NULL,
            content_hi TEXT NOT NULL,
            image_url TEXT,
            views INTEGER DEFAULT 0,
            affiliate_box_title TEXT,
            affiliate_box_desc TEXT,
            affiliate_box_url TEXT,
            affiliate_box_btn TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Seed default settings if empty
    default_settings = {
        'site_title_en': 'Global Pulse & Tech Daily',
        'site_title_hi': 'ग्लोबल पल्स एवं टेक दैनिक',
        'site_tagline_en': 'Daily Insightful Analysis on News, Politics, Finance & Science-Tech',
        'site_tagline_hi': 'समाचार, राजनीति, वित्त एवं विज्ञान-प्रौद्योगिकी का दैनिक गहन विश्लेषण',
        'adsense_client_id': 'ca-pub-1234567890123456',
        'ads_enabled': '1',
        'auto_post_schedule': 'daily', # daily automated posting
        'affiliate_disclosure_en': 'Disclosure: This post contains affiliate links. When you make a purchase or sign up through our links, we may earn an affiliate commission at no extra cost to you.',
        'affiliate_disclosure_hi': 'प्रकटीकरण: इस लेख में संबद्ध (एफिलिएट) लिंक शामिल हैं। जब आप हमारे लिंक के माध्यम से खरीदारी करते हैं या पंजीकरण करते हैं, तो हमें बिना किसी अतिरिक्त लागत के कमीशन प्राप्त हो सकता है।',
        'default_affiliate_cta': 'https://www.tradingview.com/?aff=affiliate_daily',
        'contact_email': 'editor@globalpulseaffiliate.com'
    }
    
    for key, val in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
    
    conn.commit()
    conn.close()

def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def update_setting(key, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def seed_sample_posts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM posts")
    count = cursor.fetchone()['count']
    
    if count == 0:
        sample_articles = [
            {
                "title_en": "Next-Gen Quantum Computing Breakthroughs: Transforming Global Cyber Infrastructure",
                "title_hi": "नेक्स्ट-जेन क्वांटम कंप्यूटिंग में ऐतिहासिक सफलता: वैश्विक साइबर बुनियादी ढांचे में बड़ा बदलाव",
                "slug": "quantum-computing-breakthrough-cyber-infrastructure",
                "category": "sci-tech",
                "excerpt_en": "Researchers have demonstrated error-corrected 10,000-qubit architecture, marking a monumental shift in algorithmic computing, cryptography, and artificial intelligence.",
                "excerpt_hi": "शोधकर्ताओं ने एरर-करेक्टेड 10,000-क्यूबिट आर्किटेक्चर प्रदर्शित किया है, जो एल्गोरिथम कंप्यूटिंग, क्रिप्टोग्राफी और आर्टिफिशियल इंटेलिजेंस में एक ऐतिहासिक बदलाव का संकेत है।",
                "content_en": """<p>Quantum computing has officially transitioned from laboratory experimentation to industrial scalability. In a landmark breakthrough announced this week, international research consortia have successfully synthesized fault-tolerant topological logical qubits capable of sustained coherence over record-breaking durations.</p>

<h3>Key Architectural Milestones</h3>
<p>Unlike classical binary computing relying on deterministic bit gates (0 and 1), quantum processing leverages quantum superposition and quantum entanglement. The latest breakthrough resolves the industry's longest-standing bottleneck: <strong>thermal decoherence</strong> and quantum gate error rates.</p>

<ul>
    <li><strong>Error Reduction by 99.4%:</strong> Dynamic surface codes now detect and auto-correct bit-flip errors in real time.</li>
    <li><strong>Room-Temperature Photonic Interconnects:</strong> Optical interfaces allow quantum nodes to communicate without ultra-deep cryogenic freezing.</li>
    <li><strong>Commercial Scalability:</strong> Ready for deployment across pharmaceutical drug discovery, clean energy materials, and heavy financial modeling.</li>
</ul>

<h3>Implications for Global Cybersecurity</h3>
<p>As quantum processing capacity surges, post-quantum cryptography (PQC) transitions from a theoretical standard to an urgent operational requirement. Modern financial networks, secure messaging frameworks, and sovereign databases must transition to lattice-based cryptographic algorithms before legacy RSA-4096 protocols face systematic obsolescence.</p>

<p>Industry leaders recommend upgrading enterprise infrastructure now to maintain long-term digital sovereignty.</p>""",
                "content_hi": """<p>क्वांटम कंप्यूटिंग अब आधिकारिक तौर पर प्रयोगशाला परीक्षणों से निकलकर औद्योगिक स्तर के क्रियान्वयन की दिशा में आगे बढ़ चुकी है। इस सप्ताह घोषित एक युगांतरकारी खोज में अंतरराष्ट्रीय वैज्ञानिकों के संघ ने एरर-टॉलरेंट लॉजिकल क्यूबिट्स तैयार करने में सफलता प्राप्त की है।</p>

<h3>महत्वपूर्ण तकनीकी उपलब्धियां</h3>
<p>पारंपरिक बाइनरी कंप्यूटिंग (जो 0 और 1 बिट्स पर आधारित है) के विपरीत, क्वांटम कंप्यूटिंग सुपरपोजिशन और एंटैंगलमेंट सिद्धांतों पर काम करती है। नई तकनीक ने दशकों से आ रही <strong>थर्मल डिकोहियरेंस</strong> और गेट-एरर की बाधा को पूरी तरह हल कर दिया है।</p>

<ul>
    <li><strong>त्रुटि दर में 99.4% की गिरावट:</strong> आधुनिक सरफेस कोडिंग अब रियल-टाइम में त्रुटियों को सुधारने में सक्षम है।</li>
    <li><strong>ऑप्टिकल क्वांटम नेटवर्किंग:</strong> बिना शून्य से नीचे के अत्यधिक शीतलन के भी क्वांटम नोड्स आपस में सुरक्षित डेटा साझा कर सकते हैं।</li>
    <li><strong>व्यावसायिक उपयोग:</strong> यह स्वास्थ्य क्षेत्र में नई दवाओं के निर्माण, स्वच्छ ऊर्जा बैटरी शोध और जटिल आर्थिक मॉडलिंग में क्रांतिकारी साबित होगा।</li>
</ul>

<h3>वैश्विक साइबर सुरक्षा पर इसका प्रभाव</h3>
<p>क्वांटम क्षमता में तीव्र वृद्धि के कारण पोस्ट-क्वांटम क्रिप्टोग्राफी (PQC) को अपनाना अब अति आवश्यक हो गया है। वैश्विक बैंकिंग नेटवर्क और सरकारी डेटाबेस को पुरानी एन्क्रिप्शन पद्धतियों से हटाकर आधुनिक लैटिस-आधारित सुरक्षा मानकों पर स्थानांतरित करने की दिशा में कार्य प्रारंभ हो चुका है।</p>""",
                "image_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=1200&q=80",
                "affiliate_box_title": "Top Recommended Cloud & AI Hardware",
                "affiliate_box_desc": "Accelerate your deep learning, algorithmic pipelines, and quantum emulation models with high-speed cloud TPU clusters. Exclusive promotional access available for tech developers.",
                "affiliate_box_url": "https://cloud.google.com/tpu",
                "affiliate_box_btn": "Explore Cloud AI Accelerators"
            },
            {
                "title_en": "Algorithmic Bitcoin & Forex Trading: How High-Frequency Automation Is Reshaping Currency Markets",
                "title_hi": "एल्गोरिथमिक बिटकॉइन एवं फॉरेक्स ट्रेडिंग: ऑटोमेशन कैसे बदल रहा है वैश्विक मुद्रा बाजार",
                "slug": "algorithmic-bitcoin-forex-automation-currency-markets",
                "category": "finance",
                "excerpt_en": "Discover how institutional algorithms, automated liquidity strategies, and machine learning models are dominating EUR/USD, GBP/USD, and Bitcoin (BTC) market flows.",
                "excerpt_hi": "जानिए कैसे संस्थागत एल्गोरिदम, स्वचालित लिक्विडिटी रणनीतियाँ और मशीन लर्निंग मॉडल EUR/USD, GBP/USD और बिटकॉइन (BTC) बाज़ार में नया आयाम स्थापित कर रहे हैं।",
                "content_en": """<p>The financial markets of the 2020s have undergone a decisive, permanent paradigm shift toward fully automated, algorithmic execution. Across the two most liquid instruments on Earth—Foreign Exchange (Forex) currency pairs and Bitcoin (BTC/USD)—quantitative algorithms now execute more than 85% of total aggregate volume.</p>

<h3>The Rule of Systematic Discipline</h3>
<p>Unlike human psychology prone to cognitive biases like fear of missing out (FOMO) and revenge positioning, automated trading systems strictly execute statistically validated rules. Market microstructure parameters, order book imbalances, and dynamic spread analysis allow automated algorithms to identify micro-inefficiencies and execute within microsecond latency.</p>

<h3>Core Algorithmic Architectures in Forex & Bitcoin</h3>
<ul>
    <li><strong>Statistical Arbitrage & Triangulation:</strong> Spotting temporary price divergences between major currency pairs (EUR/USD, USD/JPY, GBP/USD) and BTC trading pairs across global centralized exchanges.</li>
    <li><strong>Mean-Reversion Volatility Bands:</strong> Utilizing Bollinger adaptive envelopes and ATR filters to enter algorithmic hedges when extreme deviations occur.</li>
    <li><strong>Order Book Flow & Liquidity Detection:</strong> Machine learning models analyzing Level 2 depth of market (DoM) to predict micro-breakouts before liquidity dries up.</li>
</ul>

<h3>Risk Management: The Engine of Algorithmic Longevity</h3>
<p>Professional algorithmic developers enforce non-negotiable risk boundaries: dynamic position sizing based on portfolio Kelly criterion, maximum drawdown circuit breakers, and algorithmic hedging. For quantitative builders, reliable low-latency infrastructure and precision backtesting environments are the absolute foundation of steady risk-adjusted returns.</p>""",
                "content_hi": """<p>वित्तीय बाजारों में मानवीय निर्णयों के स्थान पर अब पूरी तरह से स्वचालित, एल्गोरिथमिक ट्रेडिंग प्रणालियों का वर्चस्व स्थापित हो चुका है। दुनिया के दो सबसे बड़े लिक्विड साधनों—विदेशी मुद्रा (Forex) जैसे EUR/USD, GBP/USD और बिटकॉइन (BTC/USD)—में आज 85% से अधिक लेन-देन पूरी तरह से स्वचालित प्रणालियों द्वारा निष्पादित किए जाते हैं।</p>

<h3>सिस्टमैटिक अनुशासन का महत्व</h3>
<p>मानवीय भावनाओं (डर, लालच और घबराहट) से मुक्त होकर, स्वचालित एल्गोरिदम केवल गणितीय और सांख्यिकीय मॉडलों पर आधारित निर्णय लेते हैं। वे माइक्रो-सेकंड की गति में बाजार के ऑर्डर बुक डेटा का विश्लेषण कर त्वरित सौदे दर्ज करते हैं।</p>

<h3>फॉरेक्स और बिटकॉइन में प्रमुख स्वचालित रणनीतियाँ</h3>
<ul>
    <li><strong>स्टैटिस्टिकल आर्बिट्राज:</strong> विभिन्न वैश्विक एक्सचेंजों पर प्रमुख करेंसी जोड़ों (EUR/USD, USD/JPY) और बिटकॉइन में क्षणिक मूल्य अंतर का लाभ उठाना।</li>
    <li><strong>मीन-रिवर्जन और वोलैटिलिटी बैंड्स:</strong> बाजार के अत्यधिक खिंचाव के समय स्वचालित हेजिंग और रिवर्सल रणनीतियों का पालन करना।</li>
    <li><strong>ऑर्डर बुक और लिक्विडिटी ट्रैकिंग:</strong> एडवांस्ड मशीन लर्निंग मॉडल जो लिक्विडिटी क्लस्टर्स को पहचानकर तुरंत जोखिम-नियंत्रित कदम उठाते हैं।</li>
</ul>

<h3>सख्त जोखिम प्रबंधन (Risk Control)</h3>
<p>पेशेवर स्वचालित प्रणालियों की सफलता का रहस्य उनके सख्त रिस्क पैरामीटर्स हैं। इनमें पूर्व-निर्धारित स्टॉप-लॉस, पोर्टफोलियो साइजिंग और ड्रॉडौन सर्किट-ब्रेकर शामिल होते हैं। एक कुशल स्वचालित ट्रेडर के लिए अत्याधुनिक बैकटेस्टिंग प्लेटफॉर्म और कम विलंबता (low latency) वाले सर्वर अनिवार्य हैं।</p>""",
                "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
                "affiliate_box_title": "Automated Charting & Quantitative Backtesting Suite",
                "affiliate_box_desc": "Build, backtest, and automate your Forex and Bitcoin algorithmic strategies with institutional-grade charting tools, multi-broker webhook execution, and real-time data feeds.",
                "affiliate_box_url": "https://www.tradingview.com",
                "affiliate_box_btn": "Claim Your Algorithmic Charting Trial"
            },
            {
                "title_en": "Global Summit 2026: Multilateral Treaties on Artificial Intelligence and Digital Borders",
                "title_hi": "वैश्विक शिखर सम्मेलन 2026: आर्टिफिशियल इंटेलिजेंस एवं डिजिटल सीमाओं पर बहुपक्षीय समझौते",
                "slug": "global-summit-multilateral-treaties-artificial-intelligence",
                "category": "politics",
                "excerpt_en": "World leaders and diplomatic envoys have finalized a landmark international governance framework balancing frontier AI safety with cross-border technological commerce.",
                "excerpt_hi": "वैश्विक नेताओं और राजनयिकों ने सीमा पार तकनीकी वाणिज्य और उन्नत AI सुरक्षा के बीच संतुलन स्थापित करने वाले एक ऐतिहासिक अंतर्राष्ट्रीय नियामक समझौते को अंतिम रूप दिया है।",
                "content_en": """<p>Representatives from 48 sovereign nations concluded high-stakes negotiations at the International Digital Sovereignty Summit today, establishing a binding global framework for ethical artificial intelligence and cross-border cryptographic governance.</p>

<h3>Core Pillars of the New Diplomatic Accord</h3>
<p>The landmark accord establishes harmonized safety benchmarks while ensuring emerging economic hubs in Asia, Europe, and the Americas retain open access to open-source algorithmic models:</p>

<ul>
    <li><strong>Autonomous Systems Accountability:</strong> Demanding verifiable transparency logs for algorithmic agents operating within critical infrastructure and healthcare.</li>
    <li><strong>Cross-Border Data Corridors:</strong> Eliminating bureaucratic tariffs on verified digital services while safeguarding citizen privacy.</li>
    <li><strong>Collaborative Energy Grid Standards:</strong> Joint public-private funding initiatives to expand carbon-neutral fusion and modular nuclear facilities powering global supercomputing clusters.</li>
</ul>

<h3>Geopolitical Realpolitik and the Tech Sphere</h3>
<p>Diplomatic analysts emphasize that technology policy is now the undisputed centerpiece of international relations. Sovereign competition is no longer fought over territorial topography alone, but rather over computational compute density, semiconductor fabs, and intellectual capital.</p>""",
                "content_hi": """<p>अंतर्राष्ट्रीय डिजिटल संप्रभुता शिखर सम्मेलन में आज 48 देशों के प्रतिनिधियों ने आर्टिफिशियल इंटेलिजेंस के नैतिक उपयोग और अंतरराष्ट्रीय डिजिटल डेटा प्रवाह पर एक ऐतिहासिक समझौते पर हस्ताक्षर किए हैं।</p>

<h3>समझौते के मुख्य बिंदु</h3>
<p>यह नया समझौता तकनीकी सुरक्षा सुनिश्चित करने के साथ-साथ विकासशील और विकसित देशों के बीच निष्पक्ष तकनीकी व्यापार को बढ़ावा देता है:</p>

<ul>
    <li><strong>स्वायत्त प्रणालियों की जवाबदेही:</strong> महत्वपूर्ण सार्वजनिक बुनियादी ढांचे और चिकित्सा में काम करने वाले AI मॉडलों के लिए कड़े सुरक्षा और ऑडिट मानक।</li>
    <li><strong>सीमा-पार डेटा गलियारे:</strong> नागरिक गोपनीयता की रक्षा करते हुए डिजिटल सेवाओं और तकनीक पर अनावश्यक व्यापारिक बाधाओं को हटाना।</li>
    <li><strong>हरित ऊर्जा और कंप्यूटिंग क्षमता:</strong> वैश्विक सुपरकंप्यूटिंग क्लस्टरों को संचालित करने के लिए पर्यावरण-अनुकूल स्वच्छ ऊर्जा और मॉड्यूलर रिएक्टरों का संयुक्त विकास।</li>
</ul>

<h3>भू-राजनीतिक दृष्टिकोण</h3>
<p>राजनयिक विश्लेषकों का मानना है कि तकनीकी नीतियां अब अंतरराष्ट्रीय संबंधों का मुख्य केंद्र बन चुकी हैं। भविष्य की वैश्विक प्रतिस्पर्धा केवल भौगोलिक सीमाओं तक सीमित नहीं है, बल्कि सेमीकंडक्टर निर्माण, कंप्यूटिंग क्षमता और बौद्धिक संपदा पर केंद्रित है।</p>""",
                "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1200&q=80",
                "affiliate_box_title": "Global Digital Security & VPN Infrastructure",
                "affiliate_box_desc": "Protect your cross-border digital identity, privacy, and online research with military-grade encrypted virtual private networks trusted by international policy analysts.",
                "affiliate_box_url": "https://nordvpn.com",
                "affiliate_box_btn": "Secure Your Digital Privacy Today"
            },
            {
                "title_en": "Breaking News: International Renewable Energy Consortium Announces 24/7 Deep-Geothermal Grid",
                "title_hi": "ताज़ा समाचार: अंतर्राष्ट्रीय नवीकरणीय ऊर्जा संघ ने 24/7 डीप-जियोथर्मल ग्रिड की घोषणा की",
                "slug": "renewable-energy-deep-geothermal-grid-announcement",
                "category": "news",
                "excerpt_en": "Commercial deployment of ultra-deep closed-loop geothermal power plants provides around-the-clock baseload clean electricity to over 15 million households.",
                "excerpt_hi": "अल्ट्रा-डीप क्लोज्ड-लूप भू-तापीय (जियोथर्मल) ऊर्जा संयंत्रों के व्यावसायिक क्रियान्वयन से 1.5 करोड़ से अधिक परिवारों को चौबीसों घंटे स्वच्छ बिजली उपलब्ध होगी।",
                "content_en": """<p>In a historic development for the global energy transition, an international green power syndicate has officially energized the first utility-scale deep geothermal grid, producing completely emissions-free baseload energy 24 hours a day, 365 days a year.</p>

<h3>Overcoming the Intermittency Problem</h3>
<p>While solar and wind generation have expanded rapidly across continents, grid operators have continually grappled with atmospheric intermittency—the absence of power on windless nights. Deep geothermal wells, drilled 5,000 meters into subterranean thermal strata, provide invariant, perpetual heat energy completely unaffected by above-ground weather patterns.</p>

<ul>
    <li><strong>Zero Water Consumption:</strong> Advanced supercritical closed-loop fluids circulate through sealed casing, eliminating aquifer contamination risk.</li>
    <li><strong>Minimal Surface Footprint:</strong> Requires less than 1% of the land area mandated by traditional utility-scale solar farms.</li>
    <li><strong>Baseload Capacity Factor:</strong> Operates at an unprecedented 96% annual uptime rating.</li>
</ul>

<p>Municipalities and industrial manufacturing zones are already queueing up to contract long-term power purchase agreements (PPAs), marking an inspiring acceleration in global decarbonization targets.</p>""",
                "content_hi": """<p>वैश्विक ऊर्जा संक्रमण की दिशा में एक क्रांतिकारी कदम उठाते हुए अंतरराष्ट्रीय हरित ऊर्जा कंसोर्टियम ने पहले वाणिज्यिक डीप-जियोथर्मल ग्रिड को सफलतापूर्वक ग्रिड से जोड़ दिया है। यह प्रणाली वर्ष के 365 दिन, 24 घंटे लगातार कार्बन-मुक्त बिजली प्रदान करेगी।</p>

<h3>सौर और पवन ऊर्जा की अनिश्चितता का स्थायी समाधान</h3>
<p>सौर और पवन ऊर्जा तेजी से बढ़ रही हैं, परंतु मौसम में बदलाव या रात के समय उत्पादन रुक जाना हमेशा एक चुनौती रहा है। इसके विपरीत, जमीन के 5,000 मीटर नीचे ड्रिल किए गए आधुनिक जियोथर्मल संयंत्र पृथ्वी के आंतरिक तापमान से अविरल ऊर्जा बनाते हैं, जिस पर मौसम का कोई असर नहीं होता।</p>

<ul>
    <li><strong>शून्य जल बर्बादी:</strong> पूरी तरह से बंद परिसंचरण (क्लोज्ड-लूप) तकनीक से भूमिगत जल स्रोतों को कोई नुकसान नहीं पहुंचता।</li>
    <li><strong>न्यूनतम भूमि की आवश्यकता:</strong> पारंपरिक सौर पार्कों की तुलना में यह 99% कम भूमि पर स्थापित किया जा सकता है।</li>
    <li><strong>96% निरंतर उत्पादन:</strong> बिना रुके लगातार बिजली आपूर्ति करने में पूरी तरह सक्षम।</li>
</ul>

<p>विभिन्न नगर पालिकाओं और औद्योगिक इकाइयों ने पहले ही इस स्वच्छ बिजली के लिए दीर्घकालिक समझौते शुरू कर दिए हैं, जो पर्यावरण संरक्षण में एक मील का पत्थर है।</p>""",
                "image_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=1200&q=80",
                "affiliate_box_title": "Eco-Friendly Portable Solar & Power Station Deals",
                "affiliate_box_desc": "Upgrade your home emergency backup and outdoor adventures with the latest high-efficiency LiFePO4 battery power stations. Clean, silent, and sustainable.",
                "affiliate_box_url": "https://ecoflow.com",
                "affiliate_box_btn": "Check Special Energy Discounts"
            }
        ]
        
        for art in sample_articles:
            cursor.execute('''
                INSERT INTO posts (
                    title_en, title_hi, slug, category, excerpt_en, excerpt_hi,
                    content_en, content_hi, image_url, affiliate_box_title,
                    affiliate_box_desc, affiliate_box_url, affiliate_box_btn
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                art['title_en'], art['title_hi'], art['slug'], art['category'],
                art['excerpt_en'], art['excerpt_hi'], art['content_en'], art['content_hi'],
                art['image_url'], art['affiliate_box_title'], art['affiliate_box_desc'],
                art['affiliate_box_url'], art['affiliate_box_btn']
            ))
        
        conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_sample_posts()
    print("Database initialized and sample posts seeded successfully!")
