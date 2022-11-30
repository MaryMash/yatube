from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
from rest_framework import status
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(text='test-text', author=self.user)

    def test_public_pages(self):
        """Проверка страниц, доступных любому пользователю"""
        public_pages_urls = ['/',
                             '/unexisting_page/',
                             '/group/test-slug/',
                             '/profile/TestUser/',
                             '/posts/' + str(self.post.pk) + '/'
                             ]

        for url in public_pages_urls:
            self.guest_client.get(url)
            with self.subTest(url=url):
                if url == '/unexisting_page/':
                    self.assertEqual(HTTPStatus.NOT_FOUND.value,
                                     status.HTTP_404_NOT_FOUND)
                else:
                    self.assertEqual(HTTPStatus.OK.value, status.HTTP_200_OK)

    def test_post_edit_page(self):
        """Страница /posts/<post_id>/edit/ доступна автору"""
        response = self.authorized_client.get('/posts/'
                                              + str(self.post.pk)
                                              + '/edit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_url(self):
        """Страница /posts/<post_id>/edit/ доступна
           авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_urls_use_correct_templates(self):
        """URL-адрес использует правильный шаблон"""
        urls_templates = {'posts/index.html': ['/'],
                          'posts/group_list.html': ['/group/test-slug/'],
                          'posts/profile.html': ['/profile/TestUser/'],
                          'posts/post_detail.html': ['/posts/'
                                                     + str(self.post.pk)
                                                     + '/'],
                          'posts/create_post.html': ['/posts/'
                                                     + str(self.post.pk)
                                                     + '/edit/',
                                                     '/create/'
                                                     ]
                          }

        for template, urls in urls_templates.items():
            for url in urls:
                with self.subTest(url=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_404_error(self):
        """Для 404 ошибки используется кастомный шаблон"""
        response = self.guest_client.get('/test123/')
        self.assertTemplateUsed(response, 'core/404.html')
