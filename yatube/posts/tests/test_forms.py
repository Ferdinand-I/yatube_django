import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase, override_settings

from posts.models import Comment, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_User'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.post_to_be_changed = Post.objects.create(
            text='Тестовый текст, надо изменить',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.logged_client = Client()
        self.logged_client.force_login(self.user)

    def test_post_appears_in_db(self):
        """Test new post appears in database and redirects after success."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 1',
            'author': self.user.username,
            'image': uploaded
        }
        response = self.logged_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_changed_with_same_id(self):
        """Test that post has the same pk after been edited."""
        post_id = self.post_to_be_changed.pk
        changed_data = {
            'text': 'Изменённый текстовый текст'
        }
        self.logged_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=changed_data
        )
        self.assertEqual(Post.objects.get(pk=post_id).text,
                         'Изменённый текстовый текст')

    def test_comment_appears_after_sending_through_comment_form(self):
        comments_count = Comment.objects.count()
        comment_form = {
            'text': 'Тестовый комментарий'
        }
        self.logged_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

