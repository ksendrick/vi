from datetime import timedelta

from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import format_html

from authapp.models import User
from delicious import settings
from newsapp.models import Article, News, Tags, TagsNews
from recipesapp.models import IngredientRecipe, RecipeSteps, Recipe, Ingredient, Category, Kitchen
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomAdminSite(admin.AdminSite):
    site_header = 'Моя административная панель'
    site_title = 'Администрирование сайта'
    index_title = 'Добро пожаловать'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context['article_count'] = Article.objects.count()
        extra_context['news_count'] = News.objects.count()


        month_labels, article_data, news_data = self.get_chart_data()
        extra_context.update({
            'month_labels': month_labels,
            'article_data': article_data,
            'news_data': news_data,
        })

        return super().index(request, extra_context)

    def get_chart_data(self):
        months = 5
        today = timezone.now()
        month_labels = []
        article_data = []
        news_data = []

        for i in range(months):
            first_day_of_month = today.replace(day=1) - timedelta(days=30*i)
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month+1, day=1) - timedelta(days=1)) if first_day_of_month.month < 12 else (first_day_of_month.replace(year=first_day_of_month.year+1, month=1, day=1) - timedelta(days=1))


            start_date = first_day_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = last_day_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)


            article_count = Article.objects.filter(created_at__range=(start_date, end_date)).count()
            news_count = News.objects.filter(created_at__range=(start_date, end_date)).count()

            month_labels.append(start_date.strftime('%b %Y'))
            article_data.append(article_count)
            news_data.append(news_count)

        month_labels.reverse()
        article_data.reverse()
        news_data.reverse()

        return month_labels, article_data, news_data

admin.site = CustomAdminSite(name='customadmin')
admin.sites.site = admin.site

admin.site.site_header = 'Моя административная панель'
admin.site.site_title = 'Администрирование сайта'
admin.site.index_title = 'Добро пожаловать'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'status_display', 'image_preview', 'created_at_formatted')
    list_display_links = ('name',)
    list_filter = ('status', 'user', 'created_at')
    search_fields = ('name', 'desc', 'user__username')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at_formatted', 'updated_at_formatted', 'image_preview_large')

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ('Изменение статуса', {
                    'fields': ('status',),
                    'description': 'Здесь вы можете изменить статус статьи'
                }),
            )

        return (
            ('Основная информация', {
                'fields': ('name', 'desc', 'img', 'video', 'user')
            }),
            ('Статус и даты', {
                'fields': ('status', 'created_at_formatted', 'updated_at_formatted'),
                'classes': ('collapse',)
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields if f.name != 'status']
        return self.readonly_fields

    def status_display(self, obj):
        status_map = {
            'news': 'Новая',
            'published': '✅ Опубликовано',
            'canceled': '❌ Отменена'
        }
        return status_map.get(obj.status, obj.status)

    status_display.short_description = 'Статус'
    status_display.admin_order_field = 'status'

    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; border: 1px solid #eee;"/>',
                obj.img.url
            )
        return "-"

    image_preview.short_description = 'Превью'

    # Большое превью в форме редактирования
    def image_preview_large(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 4px; border: 1px solid #eee;"/>',
                obj.img.url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Превью изображения'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Дата создания'

    def updated_at_formatted(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y %H:%M')

    updated_at_formatted.short_description = 'Дата обновления'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'news_count')
    search_fields = ('name',)

    def news_count(self, obj):
        return obj.tagsnews_set.filter(news__isnull=False).count()

    news_count.short_description = 'Количество новостей'


class TagsNewsInline(admin.TabularInline):
    model = TagsNews
    extra = 1
    fields = ('tags',)
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги новости'
    autocomplete_fields = ['tags']

    def get_formset(self, request, obj=None, **kwargs):
        # Ограничиваем queryset тегов при необходимости
        formset = super().get_formset(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Можно добавить дополнительные ограничения для staff
            pass
        return formset


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'image_preview', 'created_at_formatted')
    list_display_links = ('name',)
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'desc', 'user__username')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at_formatted', 'updated_at_formatted', 'image_preview_large')
    inlines = [TagsNewsInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'desc', 'user')
        }),
        ('Изображения', {
            'fields': ('img', 'img_banner', 'image_preview_large')
        }),
        ('Даты', {
            'fields': ('created_at_formatted', 'updated_at_formatted'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.img.url
            )
        return "-"

    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 300px;" />', obj.img.url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Превью изображения'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Дата создания'

    def updated_at_formatted(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y %H:%M')

    updated_at_formatted.short_description = 'Дата обновления'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=True).order_by('username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(TagsNews)
class TagsNewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'tags')
    list_filter = ('tags',)
    search_fields = ('news__name', 'tags__name')
    autocomplete_fields = ['news', 'tags']



@admin.register(Kitchen)
class KitchenAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class RecipeStepsInline(admin.TabularInline):
    model = RecipeSteps
    extra = 1
    fields = ('desc', 'img')
    verbose_name = 'Шаг рецепта'
    verbose_name_plural = 'Шаги рецепта'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    fields = ('ingredient', 'weight', 'type', 'base_servings')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'kitchen', 'time', 'image_preview', 'created_at_formatted')
    list_display_links = ('name',)
    list_filter = ('category', 'kitchen', 'created_at')
    search_fields = ('name', 'desc')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at_formatted', 'updated_at_formatted', 'image_preview_large')
    inlines = [RecipeStepsInline, IngredientRecipeInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'desc', 'time', 'category', 'kitchen')
        }),
        ('Пищевая ценность', {
            'fields': ('calories', 'proteins', 'fats', 'carbohydrates'),
            'classes': ('collapse',)
        }),
        ('Медиа', {
            'fields': ('img', 'video', 'image_preview_large')
        }),
        ('Даты', {
            'fields': ('created_at_formatted', 'updated_at_formatted'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.img.url
            )
        return "-"

    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 300px;" />',
                obj.img.url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Превью изображения'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Дата создания'

    def updated_at_formatted(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y %H:%M')

    updated_at_formatted.short_description = 'Дата обновления'


@admin.register(RecipeSteps)
class RecipeStepsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'short_desc', 'image_preview')
    list_filter = ('recipe',)
    search_fields = ('recipe__name', 'desc')

    def short_desc(self, obj):
        return obj.desc[:50] + '...' if len(obj.desc) > 50 else obj.desc

    short_desc.short_description = 'Описание'

    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.img.url
            )
        return "-"

    image_preview.short_description = 'Превью'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'weight', 'type', 'base_servings')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ['recipe', 'ingredient']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'email_confirmed')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_confirmed')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация',
         {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'img', 'img_banner')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Дополнительная информация', {'fields': (
        'email_confirmed', 'email_confirmation_code', 'receive_notifications', 'last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    actions = ['make_staff', 'remove_staff']

    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)

    make_staff.short_description = "Дать права персонала"

    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)

    remove_staff.short_description = "Забрать права персонала"




class StaffAdminSite(admin.AdminSite):
    site_header = "Панель редактора новостей"
    site_title = "Редактор новостей"
    index_title = "Управление новостями"

    def has_permission(self, request):
        return request.user.is_active and (request.user.is_superuser or request.user.is_staff)

    def admin_view(self, view, cacheable=False):
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                return redirect(f'{settings.LOGIN_URL}?next={request.path}')
            return view(request, *args, **kwargs)

        return super().admin_view(inner, cacheable)


staff_admin_site = StaffAdminSite(name='staffadmin')



@admin.register(Tags, site=staff_admin_site)
class StaffTagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'news_count')
    search_fields = ('name',)
    list_per_page = 25

    def news_count(self, obj):
        return obj.tagsnews_set.filter(news__isnull=False).count()

    news_count.short_description = 'Количество новостей'

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class StaffTagsNewsInline(admin.TabularInline):
    model = TagsNews
    extra = 1
    fields = ('tags',)
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги новости'
    autocomplete_fields = ['tags']

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(news__user=request.user)
        return qs



@admin.register(News, site=staff_admin_site)
class StaffNewsAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at_formatted', 'image_preview', 'user')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'desc')
    readonly_fields = ('created_at_formatted', 'image_preview')
    inlines = [StaffTagsNewsInline]  # The fix: Include the inline here!

    fieldsets = (
        (None, {
            'fields': ('name', 'desc', 'img', 'img_banner', 'image_preview', 'user')
        }),
    )

    def image_preview(self, obj):
        if obj.img:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.img.url)
        return "Нет изображения"

    image_preview.short_description = 'Превью'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Создано'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если это создание новой новости
            obj.user = request.user
        elif request.user.is_superuser and 'user' in form.changed_data:
            obj.user = form.cleaned_data['user']
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            new_fieldsets = []
            for name, options in fieldsets:
                if 'user' in options.get('fields', []):
                    new_fields = [f for f in options['fields'] if f != 'user']
                    new_fieldsets.append((name, {'fields': new_fields}))
                else:
                    new_fieldsets.append((name, options))
            return tuple(new_fieldsets)
        return fieldsets

    # Права доступа
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.user == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.user == request.user:
            return True
        return False

    def has_module_permission(self, request):
        return staff_admin_site.has_permission(request)



# TagsNewsAdmin для StaffAdminSite
@admin.register(TagsNews, site=staff_admin_site)
class StaffTagsNewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'tags')
    list_filter = ('tags',)
    search_fields = ('news__name', 'tags__name')
    autocomplete_fields = ['news', 'tags']
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Ограничиваем только своими новостями для staff
            qs = qs.filter(news__user=request.user)
        return qs

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.news.user == request.user:
            return True
        return False

    def has_add_permission(self, request):
        return False #  Adding only through inlines

    def has_change_permission(self, request, obj=None):
        return False # Editing only through inlines

    def has_delete_permission(self, request, obj=None):
        return False # Deleting only through inlines