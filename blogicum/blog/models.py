from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .constants import MAX_LENGTH

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('Опубликовано'),
        help_text=_('Снимите галочку, чтобы скрыть публикацию.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Добавлено')
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=('Заголовок')
    )
    description = models.TextField(
        verbose_name=('Описание')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=('Идентификатор'),
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Название места')
    )

    class Meta:
        verbose_name = _('местоположение')
        verbose_name_plural = _('Местоположения')

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name=_('Название')
    )
    text = models.TextField(
        verbose_name=_('Текст')
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Дата и время публикации'),
        help_text=_('Если установить дату и время в будущем'
                    ' — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор публикации'),
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Местоположение'),
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Категория'),
        related_name='posts'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name=_('Картинка')
    )

    class Meta:
        verbose_name = _('публикация')
        verbose_name_plural = _('Публикации')
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_full_name(self):
        return f"{self.author.first_name} {self.author.last_name}".strip()


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return (
            f'Комментарий от {self.author.username} к посту {self.post.title}'
        )
