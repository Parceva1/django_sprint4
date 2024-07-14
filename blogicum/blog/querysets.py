from django.db.models import Count, Q
from django.utils import timezone

from .models import Post


def comment_count(queryset):
    return queryset.annotate(
        comment_count=Count('comments')).order_by('-pub_date')


def get_published_posts():
    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
