from django.contrib import admin

from .models import Category, Post, Location
from .constants import LIST_PER_PAGE

admin.site.empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug',
                    'is_published', 'created_at')
    list_per_page = LIST_PER_PAGE
    list_editable = ('description', 'is_published')
    list_display_links = ('title',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category',
                    'location', 'pub_date', 'is_published', 'created_at')
    list_filter = ('category', 'location', 'is_published', 'pub_date')
    search_fields = ('title', 'text')
    list_per_page = LIST_PER_PAGE


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)
    list_per_page = LIST_PER_PAGE


admin.site.register(Location, LocationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
