import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostPages(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='Test_User'
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_slug',
            description='test_des'
        )
        for i in range(14):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group,
                image=SimpleUploadedFile(
                    name='image',
                    content=(
                        b'\x47\x49\x46\x38\x39\x61\x01\x00'
                        b'\x01\x00\x00\x00\x00\x21\xf9\x04'
                        b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
                        b'\x00\x00\x01\x00\x01\x00\x00\x02'
                        b'\x02\x4c\x01\x00\x3b'
                    ),
                    content_type='image/gif'
                )
            )
        cls.group_wrong = Group.objects.create(
            title='wrong_group_title',
            slug='wrong_slug'
        )
        cls.user_following = User.objects.create(
            username='Following'
        )
        cls.post_following = Post.objects.create(
            text='Текст following',
            author=cls.user_following,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_following
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """Test pages use correct templates."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group-list',
                kwargs={'slug': 'test_slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'Test_User'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/update_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Test index page context."""
        context_dict = {
            'title': 'Последние обновления на сайте',
            'description': 'Последние обновления на сайте'
        }
        response = self.authorized_client.get(reverse('posts:index'))
        for context, value in context_dict.items():
            with self.subTest(value=context):
                self.assertEqual(response.context[context], value)

    def test_first_page_contains_ten_posts(self):
        """Test paginator on pages where needed with settings page count."""
        pages_with_paginators = {
            'index': reverse('posts:index'),
            'group-list': reverse(
                'posts:group-list',
                kwargs={'slug': 'test_slug'}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': 'Test_User'}
            )
        }
        for page in pages_with_paginators:
            response = self.authorized_client.get(pages_with_paginators[page])
            with self.subTest():
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.PAGE_COUNTS
                )

    def test_group_posts_correct_context(self):
        """Test group post page has correct context."""
        response = self.authorized_client.get(
            reverse('posts:group-list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'].slug, 'test_slug')
        self.assertEqual(response.context['group'].title, 'test_group_title')
        self.assertEqual(response.context['group'].description, 'test_des')

    def test_profile_posts_correct_context(self):
        """Test profile page got correct context."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Test_User'})
        )
        self.assertEqual(
            response.context['profile_info'].posts.all().count(),
            14
        )
        self.assertEqual(
            response.context['profile_info'].get_full_name(),
            ''
        )

    def test_post_detail_correct_context(self):
        """Post detail teplate is formed with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(response.context['post'].text, 'Тестовый текст')
        self.assertEqual(response.context['post'].author.username, 'Test_User')
        self.assertEqual(response.context['post'].group.title,
                         'test_group_title')

    def test_create_post_correct_form_fields_type(self):
        """Test fields of create post form have coorect type."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        """Test post edit page has correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].text,
                         'Тестовый текст')
        self.assertEqual(response.context['post'].author.username,
                         'Test_User')
        self.assertEqual(response.context['post'].group.title,
                         'test_group_title')

    def test_new_post_appears_on_right_pages(self):
        """Test new post appears on top of correct pages."""
        pages = {
            'posts:index': {},
            'posts:group-list': {'slug': 'test_slug'},
            'posts:profile': {'username': 'Test_User'}
        }
        for page, kwargs in pages.items():
            response = self.authorized_client.get(
                reverse(
                    page,
                    kwargs=kwargs
                )
            )
            post = response.context['page_obj'][0]
            with self.subTest():
                self.assertEqual(post.text, 'Тестовый текст')
                self.assertEqual(post.author.username, 'Test_User')
                self.assertEqual(post.group.title, 'test_group_title')

    def test_new_post_not_appears_in_wrong_group(self):
        """Test new post does not appear in wrong group."""
        response = self.authorized_client.get(
            reverse(
                'posts:group-list',
                kwargs={'slug': 'wrong_slug'}
            )
        )
        post = response.context['page_obj']
        self.assertEqual(len(post), 0)

    def test_image_appears_in_context(self):
        """Test that context has an image."""
        pages = (
            reverse('posts:index'),
            reverse(
                'posts:group-list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )
        for page in pages:
            response = self.authorized_client.get(page)
            context = response.context['page_obj'][0]
            with self.subTest(context=context):
                self.assertTrue(context.image)

    def test_image_appears_in_post_detail_context(self):
        """Test that context has an image."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        context = response.context['post']
        self.assertTrue(context.image)

    def test_cache_index(self):
        new_post = Post.objects.create(
            text='delete',
            author=self.user
        )
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        content = response.content
        Post.objects.filter(pk=new_post.id).delete()
        Post.objects.create(
            text='delete_2',
            author=self.user
        )
        response_del = self.authorized_client.get(
            reverse('posts:index')
        )
        content_del = response_del.content
        self.assertEqual(content, content_del)

    def test_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}
                    )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user
            )
        )

    def test_unfollow(self):
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_following.username}
                    )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_following
            )
        )

    def test_post_appears_in_follow(self):
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        context = response.context['page_obj'][0]
        self.assertEqual(context.text, self.post_following.text)

    def test_post_not_appears_in_wrong_follow(self):
        self.authorized_client.force_login(self.user_following)
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        context = response.context['page_obj']
        self.assertEqual(len(context), 0)
