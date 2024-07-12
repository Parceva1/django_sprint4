from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileEditForm
from .constants import LIST_PER_PAGE


def get_recent_posts(request=None):
    posts = Post.objects.filter(
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments'))

    if request and request.user.is_authenticated:
        posts = posts | Post.objects.filter(
            author=request.user,
            is_published=False
        )
    return posts.filter(is_published=True).distinct()


def index(request):
    template = 'blog/index.html'
    posts = get_recent_posts(request).order_by('-pub_date')
    paginator = Paginator(posts, LIST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def category_posts(request, slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=slug,
        is_published=True,
        created_at__lte=timezone.now()
    )

    posts = get_filtered_posts(request).filter(
        category=category,
        pub_date__lte=timezone.now()  # Добавляем фильтр по дате публикации
    )

    paginator = Paginator(posts, LIST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def get_filtered_posts(request=None):
    posts = Post.objects.filter(
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    if request and request.user.is_authenticated:
        posts = posts | Post.objects.filter(author=request.user)
    return posts.filter(is_published=True).distinct()


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=pk)
    if not post.is_published and post.author != request.user:
        raise get_object_or_404(Post, pk=404)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация успешно добавлена!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Публикация успешно отредактирована!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=post.pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html',
                  {'form': PostForm(instance=post)})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-pub_date').annotate(
        comment_count=Count('comments')
    )

    if request.user == user:
        is_owner = True
    else:
        is_owner = False

    paginator = Paginator(posts, LIST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'is_owner': is_owner,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', pk=post_id)
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'includes/comments.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
