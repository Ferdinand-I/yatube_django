from django.test import Client, TestCase

from http import HTTPStatus


class AboutUrlTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_static_pages(self):
        tamplates = [
            '/about/author/',
            '/about/tech/'
        ]
        for page in tamplates:
            response = self.client.get(page)
            with self.subTest(value=page):
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
