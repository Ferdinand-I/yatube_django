from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


User = get_user_model()


class GroupModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='maniac',
            slug='maniac'
        )

    def test_str_name(self):
        """Test correct str-view."""
        group = self.group
        expected = 'maniac'
        self.assertEqual(group.__str__(), expected)


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый длинный пост',
        )

    def test_model_has_correct_str_name(self):
        """Test correct str-view."""
        post = self.post
        expected = 'Тестовый длинны'
        self.assertEqual(post.__str__(), expected)

    def test_verbose_name(self):
        """Test correct verbose names of model's fields."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Test correct help texts of model's fields."""
        post = self.post
        field_help = {
            'text': 'Введите текс поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
