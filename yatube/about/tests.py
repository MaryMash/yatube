from django.test import Client, TestCase
from django.urls import reverse


class AbouURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_public_pages(self):
        """Проверка страниц, доступных любому пользователю"""
        public_pages_urls = ['/about/author/', '/about/tech/']

        for url in public_pages_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_templates(self):
        """URL-адрес использует правильный шаблон"""
        template_urls_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        for url, template in template_urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class AboutViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_use_correct_template(self):
        """Страницы используют правильные шаблоны"""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
