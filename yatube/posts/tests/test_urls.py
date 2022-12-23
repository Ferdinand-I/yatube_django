from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import reverse
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_Username')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user
        )
        cls.group = Group.objects.create(
            slug='qwerty'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_guests_exists(self):
        """Test pages' response status after non-logged user request."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group-list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        ]
        for page in pages:
            response = self.guest_client.get(page)
            with self.subTest():
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_404_page(self):
        """Test 404 response for unexisting page request."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_create_post_for_authorized_client_exists(self):
        """Test page with post creation is
        availible for authorized user.
        """
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_create_post_for_guest_client_redirects(self):
        """Test correct redirection from creating
        post if user is not logged.
        """
        response = self.guest_client.get(
            reverse('posts:post_create'),
            follow=True)
        self.assertRedirects(response, reverse('users:login'))

    def test_edit_post_exists(self):
        """Test edit post page is availible for
        authorized user.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_use_correct_template(self):
        """URLs use correct template."""
        cache.clear()
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group-list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
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
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_comments_url_is_availible_only_for_authorized_users(self):
        """Test unauthorized user redirects to login page
        if tries to get comment page.
        """
        page = reverse('posts:add_comment',
                       kwargs={'post_id': self.post.id})
        response = self.guest_client.get(page)
        self.assertRedirects(
            response,
            reverse('users:login') + f'?next={page}'
        )
