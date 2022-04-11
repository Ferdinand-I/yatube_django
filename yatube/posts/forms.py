from django.forms import ModelForm

from posts.models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = {'text', 'group', 'image'}
    field_order = ['text', 'group', 'image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = {'text',}