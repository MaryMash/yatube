import shutil
import tempfile
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from ..models import Group, Post, Follow
from ..constants import PER_PAGE

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        for i in range(1, 3):
            Group.objects.create(
                title='Test title ' + str(i),
                slug='test-slug-' + str(i),
                description='Test description ' + str(i)
            )

        for i in range(1, 12):
            Post.objects.create(
                text='Test text ' + str(i),
                author=self.user,
                group=Group.objects.get(id=1)
            )

        self.post = Post.objects.create(
            text='Test text 12',
            author=self.user,
            group=Group.objects.get(id=2)
        )

        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.image_post = Post.objects.create(
            text='Тестовый пост с картинкой',
            author=self.user,
            group=Group.objects.get(id=1),
            image=uploaded
        )

    def test_pages_use_correct_template(self):
        """URL-адрес использует правильный шаблон"""

        templates_pages = {
            'posts/index.html': [reverse('posts:index')],
            'posts/group_list.html': [reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug-1'})],
            'posts/profile.html': [reverse('posts:profile',
                                           kwargs={'username': 'TestUser'})],
            'posts/post_detail.html': [reverse('posts:post_detail',
                                               kwargs={'post_id': 1}
                                               )],
            'posts/create_post.html': [reverse('posts:post_edit',
                                               kwargs={'post_id': 1}
                                               ),
                                       reverse('posts:post_create')]
        }

        for template, reverse_names in templates_pages.items():
            for name in reverse_names:
                with self.subTest(reverse_name=name):
                    response = self.authorized_client.get(name)
                    self.assertTemplateUsed(response, template)

    def test_main_page_shows_correct_number_of_posts(self):
        """На главной странице отображается правильное кол-во постов"""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        response_2 = self.authorized_client.get(reverse('posts:index')
                                                + '?page=2')
        total_posts = (len(response_1.context['page_obj'])
                       + len(response_2.context['page_obj']))
        self.assertEqual(len(response_1.context['page_obj']), PER_PAGE)
        self.assertEqual(len(response_2.context['page_obj']), total_posts
                         - PER_PAGE)

    def test_group_page_shows_correct_number_of_posts(self):
        """На странице группы отображается правильное кол-во постов"""
        response_1 = self.authorized_client.get(reverse('posts:group_list',
                                                kwargs={
                                                    'slug': 'test-slug-1'
                                                }))
        response_2 = self.authorized_client.get(reverse('posts:group_list',
                                                kwargs={'slug': 'test-slug-1'})
                                                + '?page=2')
        total_posts = (len(response_1.context['page_obj'])
                       + len(response_2.context['page_obj']))
        self.assertEqual(len(response_1.context['page_obj']), PER_PAGE)
        self.assertEqual(len(response_2.context['page_obj']), total_posts
                         - PER_PAGE)

    def test_profile_page_shows_correct_number_of_posts(self):
        """На странице профиля отображается правильное кол-во постов"""
        response_1 = self.authorized_client.get(reverse('posts:profile',
                                                kwargs={
                                                    'username': 'TestUser'
                                                }))
        response_2 = self.authorized_client.get(reverse('posts:profile',
                                                kwargs={
                                                    'username': 'TestUser'
                                                })
                                                + '?page=2')
        total_posts = (len(response_1.context['page_obj'])
                       + len(response_2.context['page_obj']))
        self.assertEqual(len(response_1.context['page_obj']), PER_PAGE)
        self.assertEqual(len(response_2.context['page_obj']), total_posts
                         - PER_PAGE)

    def test_detail_page_shows_correct_post(self):
        """На старнице posts/post_id показывается правильный пост"""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={
                                                  'post_id': 1
                                              }))
        post_text = response.context['post'].text
        post_author = response.context['post'].author.username
        post_group = response.context['post'].group.title
        post_1 = Post.objects.get(id=1)

        self.assertEqual(post_text, post_1.text)
        self.assertEqual(post_author, post_1.author.username)
        self.assertEqual(post_group, post_1.group.title)

    def test_create_page_shows_form(self):
        """На странице posts/create отображается форма создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField
        }

        for field, format in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, format)

    def test_post_with_group_is_shown(self):
        """Пост с группой показывается на главной, стр. профиля
           и на стр. группы"""
        resp_main = self.authorized_client.get(reverse('posts:index'))
        post_text_main = resp_main.context['page_obj'][2].text
        resp_grp = self.authorized_client.get(reverse(
                                              'posts:group_list',
                                              kwargs={'slug': 'test-slug-1'}))
        post_text_group = resp_grp.context['posts'][1].text
        resp_prf = self.authorized_client.get(reverse(
                                              'posts:profile',
                                              kwargs={'username': 'TestUser'}))
        post_text_prf = resp_prf.context['post'].author.posts.get(id=11).text
        post_11 = Post.objects.get(id=11)
        self.assertEqual(post_text_main, post_11.text)
        self.assertEqual(post_text_group, post_11.text)
        self.assertEqual(post_text_prf, post_11.text)

    def test_post_is_in_correct_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        response = self.authorized_client.get(reverse(
                                              'posts:group_list',
                                              kwargs={'slug': 'test-slug-2'}))
        post = response.context['posts'][0]
        post_11 = Post.objects.get(id=11)
        self.assertNotEqual(post.text, post_11.text)

    def test_post_with_impage(self):
        """Изображение передается в словаре context на главной странице,
           странице профайла, странице группы, странице поста"""
        main = self.authorized_client.get(reverse('posts:index'))
        image_main = main.context['page_obj'][0].image
        profile = self.authorized_client.get(reverse(
                                             'posts:profile',
                                             kwargs={'username': 'TestUser'}))
        image_profile = profile.context['page_obj'][0].image
        group = self.authorized_client.get(reverse(
                                           'posts:group_list',
                                           kwargs={'slug': 'test-slug-1'}))
        image_group = group.context['page_obj'][0].image
        post = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.image_post.pk}))
        image_post = post.context['post'].image

        self.assertIsInstance(image_main, ImageFieldFile)
        self.assertIsInstance(image_profile, ImageFieldFile)
        self.assertIsInstance(image_group, ImageFieldFile)
        self.assertIsInstance(image_post, ImageFieldFile)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NewUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_cache(self):
        """Проверяем кэширование на главной странице"""
        response_1 = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.all()[0]
        post_1.text = 'Новый тестовый текст'
        post_1.save()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))

        self.assertEqual(response_1.content, response_2.content)
        self.assertNotEqual(response_1.content, response_3.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест подписок'
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Follower')
        self.user_2 = User.objects.create_user(username='NotFollower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_following = Client()
        self.not_following.force_login(self.user_2)

    def test_following(self):
        """Проверяем, что авторизованный пользователь может подписываться
        на др. пользователей"""
        response = self.authorized_client.get(reverse(
                                              'posts:profile_follow',
                                              kwargs={
                                                  'username': 'TestUser'
                                              }))

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_ufollowing(self):
        """Проверяем, что авторизованный пользователь может отписываться
        от пользователей"""
        response = self.authorized_client.get(reverse(
                                              'posts:profile_unfollow',
                                              kwargs={
                                                  'username': 'TestUser'
                                              }))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_feed(self):
        """Проверяем, что Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(user=self.user, author=FollowTest.user)
        response_1 = self.authorized_client.get(reverse('posts:follow_index'))
        post_text = response_1.context['page_obj'][0].text
        response_1 = self.authorized_client.get(reverse('posts:follow_index'))
        cache.clear()
        response_2 = self.not_following.get(reverse('posts:follow_index'))
        self.assertEqual(post_text, FollowTest.post.text)
        self.assertNotContains(response_2, FollowTest.post.text)
