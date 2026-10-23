import unittest
from app import app
from database import get_db

class TestGoogleAffiliateBlog(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Global Pulse', response.data)

    def test_bilingual_home_hindi(self):
        response = self.app.get('/?lang=hi')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT slug FROM posts LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        slug = row['slug']
        
        response = self.app.get(f'/post/{slug}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Read in English', response.data)
        self.assertIn(b'affiliate-article-spotlight', response.data)

    def test_category_pages(self):
        for cat in ['news', 'politics', 'finance', 'sci-tech']:
            response = self.app.get(f'/category/{cat}')
            self.assertEqual(response.status_code, 200)

    def test_admin_page(self):
        # Without login: must redirect to login page
        response = self.app.get('/admin')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.headers['Location'])

        # With valid password: must succeed
        login_res = self.app.post('/admin/login', data={'password': 'admin@Pulse2026'}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Admin & Daily Blog Operations Console', login_res.data)

    def test_api_generate_test_post(self):
        # Log in first
        self.app.post('/admin/login', data={'password': 'admin@Pulse2026'})
        response = self.app.post('/api/generate-test-post', json={'category': 'finance'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['post']['category'], 'finance')

    def test_sitemap_and_feed(self):
        res_sitemap = self.app.get('/sitemap.xml')
        self.assertEqual(res_sitemap.status_code, 200)
        self.assertIn(b'<urlset', res_sitemap.data)

        res_feed = self.app.get('/feed.xml')
        self.assertEqual(res_feed.status_code, 200)
        self.assertIn(b'<rss version="2.0"', res_feed.data)

    def test_compliance_pages(self):
        for page in ['/privacy-policy', '/terms', '/affiliate-disclosure', '/about', '/contact']:
            res = self.app.get(page)
            self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
