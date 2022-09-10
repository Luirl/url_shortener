import unittest
import json
from main import app
import os.path


class TestStringMethods(unittest.TestCase):


    def test_url_shortener_GET(self):
        tester = app.test_client(self)
        response = tester.get('/shorten_url')
        self.assertEqual(response.status_code, 400)


    def test_url_shortener_OK(self):
        tester = app.test_client(self)
        response = tester.post('/shorten_url',
                               data=json.dumps(dict(url='http:///test.com')),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(b'shortened_url' in response.data)


    def test_url_shortener_NoJSON(self):
        tester = app.test_client(self)
        response = tester.post('/shorten_url',
                               data='http:///test.com')
        self.assertEqual(response.status_code, 400)


    def test_url_shortener_NoUrlInJSON(self):
        tester = app.test_client(self)
        response = tester.post('/shorten_url',
                               data=json.dumps(dict(other_tag='http:///test.com')),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


    def test_url_shortener_EmptyURL(self):
        tester = app.test_client(self)
        response = tester.post('/shorten_url',
                               data=json.dumps(dict(url='')),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


    def test_url_shortener_TwiceSameShortened(self):
        tester = app.test_client(self)
        response1 = tester.post('/shorten_url',
                               data=json.dumps(dict(url='http:///test.com')),
                               content_type='application/json')

        response2 = tester.post('/shorten_url',
                               data=json.dumps(dict(url='http:///test.com')),
                               content_type='application/json')

        short_url1, short_url2 = response1.json["shortened_url"], response2.json["shortened_url"]

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertTrue(short_url1 == short_url2)


    def test_get_original_url_OK(self):
        tester = app.test_client(self)
        response = tester.post('/shorten_url',
                               data=json.dumps(dict(url='http:///test.com')),
                               content_type='application/json')

        if response.status_code == 201:
            short_code = os.path.basename(response.json["shortened_url"])

            response = tester.get('/' + short_code)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'original_url' in response.data)


    def test_get_original_url_NotPresent(self):
        tester = app.test_client(self)
        response = tester.get('/ShortCodeThatDoesNotExist')
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()