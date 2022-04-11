from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render)
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@cache_page(20)
def index(request: HttpRequest) -> HttpResponse:
    """View-Function returns rendered html-view
    with ten(10) last posts.
    """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_COUNTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    description = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
        'description': description
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View-Function returns rendered html-view
    with posts which do belong to a certain group.
    """
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title.capitalize()}'
    posts = Post.objects.filter(group=group).all()
    paginator = Paginator(posts, settings.PAGE_COUNTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    description = 'Записи сообщества '
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
        'description': description
    }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """View-Function returns rendered
    html-view with a profile info.
    """
    user = request.user
    profile_info = get_object_or_404(User, username=username)
    title = f'Профайл пользователя {profile_info.get_full_name()}'
    posts = profile_info.posts.all()
    paginator = Paginator(posts, settings.PAGE_COUNTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    following = True
    if user.is_authenticated:
        if Follow.objects.filter(user=user, author=profile_info):
            following = False
    context = {
        'profile_info': profile_info,
        'title': title,
        'page_obj': page_obj,
        'following': following,
        'user': user
    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """View-Function returns rendered
    html-view with a post details.
    """
    form = CommentForm()
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post).all()
    if len(post.text) > 20:
        title = post.text[:20] + '...'
    else:
        title = post.text
    context = {
        'title': title,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request: HttpRequest) -> HttpResponse:
    """View-Function returns rendered
    html-view with a form to create a post.
    """
    if request.user.is_authenticated is not True:
        return redirect('/auth/login/')
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(False)
    post.author = request.user
    post.save()
    return redirect(f'/profile/{request.user}/')


def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """View-Function returns rendered
    html-view with a form to edit a post.
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect(f'/posts/{post_id}')
    if request.method != 'POST':
        form = PostForm(
            files=request.FILES or None,
            instance=post
        )
        return render(request,
                      'posts/update_post.html',
                      {'form': form, 'post': post})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.author = request.user
    post.save()
    return redirect(f'/posts/{post_id}/')


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """View-function that creates comments
     and redirects to post details' page.
     """
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """View-function returns view with posts list of following authors."""
    followings = request.user.follower.all()
    lst_of_followings = []
    for following in followings:
        lst_of_followings.append(following.author)
    posts = Post.objects.filter(author__in=lst_of_followings)
    paginator = Paginator(posts, settings.PAGE_COUNTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Подписки'
    description = 'Все посты пользователей, на которых вы подписаны'
    context = {
        'page_obj': page_obj,
        'title': title,
        'description': description
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """View-function to follow author."""
    author = User.objects.get(username=username)
    following = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if author != request.user and not following:
        Follow.objects.create(
            user=request.user,
            author=author
        )
        return redirect('posts:profile', username=username)
    else:
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """View-function to unfollow author."""
    author = User.objects.get(username=username)
    following_existing = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if following_existing:
        following = Follow.objects.get(user=request.user, author=author)
        following.delete()
        return redirect('posts:profile', username=username)
    else:
        return redirect('posts:profile', username=username)
