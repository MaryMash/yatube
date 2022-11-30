from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тесовый текст'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        post_str = post.__str__()
        self.assertEqual(post_str, post.text[:15])

        group = PostModelTest.group
        group_str = group.__str__()
        self.assertEqual(group_str, group.title)

    def test_group_verbose_name(self):
        """Проверяем verbose_name у модели Group"""
        group = PostModelTest.group
        field_verboses_group = {
            'title': 'Название',
            'slug': 'Адрес страницы',
            'description': 'Описание'
        }

        for field, value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, value
                )

    def test_group_verbose_name(self):
        """Проверяем verbose_name у модели Post"""
        post = PostModelTest.post
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, value
                )

    def test_group_help_text(self):
        """Проверяем help_text у модели Group"""
        group = PostModelTest.group
        field_help_texts_group = {
            'title': 'Название группы',
            'slug': 'Адрес страницы группы',
            'description': 'Описание группы'
        }

        for field, value in field_help_texts_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, value
                )

    def test_post_help_text(self):
        """Проверяем help_text у модели Post"""
        post = PostModelTest.post
        field_help_texts_post = {
            'text': 'Текст нового поста',
            'pub_date': 'День, когда был опубликован пост',
            'author': 'Автор поста',
            'group': 'Группа, к которой относится пост'
        }

        for field, value in field_help_texts_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, value
                )
