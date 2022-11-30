import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from ..models import Group, Post, Comment
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="No name")
        Post.objects.create(
            text='Test text',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Test text 2',
            author=self.user
        )
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'

        )

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Created post text'}
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {'text': 'Changed text'}
        last_post = Post.objects.latest('id')
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': last_post.id}),
            data=form_data,
            follow=True
        )
        last_post.refresh_from_db()

        self.assertEqual(last_post.text, form_data['text'])

    def test_post_with_image(self):
        """Проверяем создание поста с картинкой"""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост с картинкой',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост с картинкой',
                image='posts/small.gif'
            ).exists()
        )

    def test_comment(self):
        """Проверяем, что комментарий появляется на странице поста
        и что могут оставлять только авторизованные пользователи"""
        form_data = {'text': 'Test comment'}

        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}
                    ),
            data=form_data,
            follow=True
        )
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}
                    ),
            data=form_data,
            follow=True
        )

        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id': self.post.id})
                                              )
        comment_text = response.context['comments'].last().text
        self.assertEqual(comment_text, form_data['text'])
        self.assertEqual(Comment.objects.all().count(), 1)
