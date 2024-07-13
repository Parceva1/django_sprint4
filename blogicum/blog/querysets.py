from django.db.models import Count, Q
from django.utils import timezone

from .models import Post


def comment_count(queryset):
    return queryset.annotate(comment_count=Count('comments'))


def get_published_posts(request=None):
    if request and request.user.is_authenticated:
        queryset = Post.objects.all()
        queryset = queryset.filter(
            Q(is_published=True) | Q(author=request.user))
    else:
        queryset = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now())

    return comment_count(queryset.order_by('-pub_date'))
