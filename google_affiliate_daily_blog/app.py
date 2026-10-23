from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import os
from datetime import datetime, timezone
from database import init_db, seed_sample_posts, get_db, get_settings, update_setting
from generator import generate_post, start_scheduler_thread

app = Flask(__name__)
app.secret_key = 'google-affiliate-daily-bilingual-secret'

# Initialize database and seed sample posts
init_db()
seed_sample_posts()

# Start background automated scheduler
start_scheduler_thread()

CATEGORY_META = {
    'news': {
        'name_en': 'World News',
        'name_hi': 'ताज़ा समाचार',
        'icon': '📰',
        'badge_class': 'badge-news'
    },
    'politics': {
        'name_en': 'Politics & Policy',
        'name_hi': 'राजनीति एवं कूटनीति',
        'icon': '🏛️',
        'badge_class': 'badge-politics'
    },
    'finance': {
        'name_en': 'Algorithmic Finance & BTC',
        'name_hi': 'एल्गोरिथमिक वित्त एवं BTC',
        'icon': '💹',
        'badge_class': 'badge-finance'
    },
    'sci-tech': {
        'name_en': 'Science & Technology',
        'name_hi': 'विज्ञान और प्रौद्योगिकी',
        'icon': '🔬',
        'badge_class': 'badge-tech'
    }
}

@app.context_processor
def inject_globals():
    lang = request.args.get('lang') or request.cookies.get('site_lang', 'en')
    settings = get_settings()
    return dict(
        lang=lang,
        settings=settings,
        categories=CATEGORY_META,
        current_year=datetime.now().year
    )

@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 12")
    posts = cursor.fetchall()
    
    # Featured post (latest one)
    featured = posts[0] if posts else None
    latest_posts = posts[1:] if len(posts) > 1 else []
    
    # Category highlights
    category_posts = {}
    for cat in CATEGORY_META.keys():
        cursor.execute("SELECT * FROM posts WHERE category = ? ORDER BY created_at DESC LIMIT 3", (cat,))
        category_posts[cat] = cursor.fetchall()
        
    conn.close()
    return render_template('index.html', featured=featured, latest_posts=latest_posts, category_posts=category_posts)

@app.route('/post/<slug>')
def post_detail(slug):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE slug = ?", (slug,))
    post = cursor.fetchone()
    
    if not post:
        conn.close()
        return "Post not found", 404
        
    # Increment views
    cursor.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post['id'],))
    conn.commit()
    
    # Related posts
    cursor.execute("SELECT * FROM posts WHERE category = ? AND id != ? ORDER BY created_at DESC LIMIT 3", (post['category'], post['id']))
    related = cursor.fetchall()
    conn.close()
    
    return render_template('post.html', post=post, related=related)

@app.route('/category/<cat_slug>')
def category_view(cat_slug):
    if cat_slug not in CATEGORY_META:
        return "Category not found", 404
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE category = ? ORDER BY created_at DESC", (cat_slug,))
    posts = cursor.fetchall()
    conn.close()
    
    return render_template('category.html', cat_slug=cat_slug, cat_meta=CATEGORY_META[cat_slug], posts=posts)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    posts = []
    if query:
        conn = get_db()
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT * FROM posts 
            WHERE title_en LIKE ? OR title_hi LIKE ? OR excerpt_en LIKE ? OR excerpt_hi LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))
        posts = cursor.fetchall()
        conn.close()
    return render_template('search.html', query=query, posts=posts)

@app.route('/set-lang/<lang_code>')
def set_language(lang_code):
    if lang_code not in ['en', 'hi']:
        lang_code = 'en'
    ref = request.referrer or url_for('home')
    resp = make_response(redirect(ref))
    resp.set_cookie('site_lang', lang_code, max_age=365*24*60*60)
    return resp

# Legal & Compliance pages for Google AdSense Approval
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('pages/privacy.html')

@app.route('/terms')
def terms():
    return render_template('pages/terms.html')

@app.route('/affiliate-disclosure')
def affiliate_disclosure():
    return render_template('pages/disclosure.html')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/contact')
def contact():
    return render_template('pages/contact.html')

# Admin Portal
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save_settings':
            update_setting('site_title_en', request.form.get('site_title_en', ''))
            update_setting('site_title_hi', request.form.get('site_title_hi', ''))
            update_setting('adsense_client_id', request.form.get('adsense_client_id', ''))
            update_setting('ads_enabled', '1' if request.form.get('ads_enabled') else '0')
            update_setting('default_affiliate_cta', request.form.get('default_affiliate_cta', ''))
            update_setting('contact_email', request.form.get('contact_email', ''))
            return redirect(url_for('admin', success="Settings saved successfully!"))
            
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as total_posts, SUM(views) as total_views FROM posts")
    stats = cursor.fetchone()
    conn.close()
    
    settings = get_settings()
    return render_template('admin.html', posts=posts, stats=stats, settings=settings)

@app.route('/api/generate-test-post', methods=['POST'])
def api_generate_test():
    category = request.json.get('category') if request.is_json else request.form.get('category')
    new_post = generate_post(category if category in CATEGORY_META else None)
    return jsonify({
        "success": True,
        "message": "Daily test blog post created successfully!",
        "post": new_post
    })

@app.route('/admin/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', success="Post deleted successfully!"))

# SEO: Sitemap and RSS
@app.route('/sitemap.xml')
def sitemap():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT slug, created_at FROM posts ORDER BY created_at DESC")
    posts = cursor.fetchall()
    conn.close()
    
    base_url = request.url_root.rstrip('/')
    xml_content = render_template('sitemap.xml', posts=posts, base_url=base_url)
    resp = make_response(xml_content)
    resp.headers['Content-Type'] = 'application/xml'
    return resp

@app.route('/feed.xml')
def feed():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 20")
    posts = cursor.fetchall()
    conn.close()
    
    base_url = request.url_root.rstrip('/')
    xml_content = render_template('feed.xml', posts=posts, base_url=base_url, now=datetime.now(timezone.utc))
    resp = make_response(xml_content)
    resp.headers['Content-Type'] = 'application/rss+xml'
    return resp

@app.route('/robots.txt')
def robots():
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {request.url_root.rstrip('/')}/sitemap.xml
"""
    resp = make_response(content)
    resp.headers['Content-Type'] = 'text/plain'
    return resp

if __name__ == '__main__':
    print("Starting Google Affiliate Bilingual Blog Server...")
    print("Serving on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
