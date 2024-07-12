from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_published_posts():
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def get_user_posts(user):
    return Post.objects.filter(author=user)
