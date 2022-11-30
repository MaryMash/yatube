from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_public_urls(self):
        """Страницы доступны любому пользователю."""
        public_pages_urls = ['/auth/logout/',
                             '/auth/signup/',
                             '/auth/login/',
                             '/auth/password_reset/']

        for url in public_pages_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_template(self):
        """Страницы используют правильные шаблоны. """
        urls_templates = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html'
        }

        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class UsersViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_use_correct_template(self):
        """Страницы используют правильные шаблоны"""
        template_pages_names = {
            'users/logged_out.html': reverse('users:logout'),
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login')
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_shows_form(self):
        """На страницу /users/signup передается форма"""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class UsersFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('Test user 1')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_user(self):
        """Валидная форма создает нового пользователя"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'username': 'Test_user_2',
            'email': 'test@test.ru',
            'password1': '98765432@',
            'password2': '98765432@',
        }
        self.authorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
