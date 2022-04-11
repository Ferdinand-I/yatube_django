from django.contrib import admin
from .models import Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'image'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description'
    )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    list_editable = ('author',)
