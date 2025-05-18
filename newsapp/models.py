from django.core.validators import FileExtensionValidator
from django.db import models
from tinymce.models import HTMLField

from authapp.models import User

class Tags(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        db_table = 'tags'
        permissions = [
            ("can_use_tags", "Может использовать теги"),
        ]


class News(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)
    img = models.ImageField(
        verbose_name='Изображение',
        upload_to='img_news/%Y/%m/%d',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg', 'webp'])],
        null=True
    )
    img_banner = models.ImageField(
        verbose_name='Изображение баннера',
        upload_to='img_banner/%Y/%m/%d',
        default='img_banner/fon.png',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg', 'webp'])],
        null=True
    )
    desc = HTMLField(verbose_name='Описание')
    likes = models.ManyToManyField(User, related_name='liked_news', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        db_table = 'news'


class Article(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    desc = HTMLField(verbose_name='Описание')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    likes = models.ManyToManyField(User, related_name='liked_article', blank=True)
    img = models.ImageField(
        verbose_name='Изображение',
        upload_to='article/%Y/%m/%d',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg', 'webp'])],
    )
    STATUS_CHOICES = [
        ('news', 'Новая'),
        ('published', 'Опубликовано'),
        ('canceled', 'Отменена'),
    ]
    status = models.CharField(verbose_name='Статус', choices=STATUS_CHOICES, default='news', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    def status_ru(self):
        status = dict(self.STATUS_CHOICES)
        return status.get(self.status, self.status)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        db_table = 'article'


class TagsNews(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Новости', null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статьи', null=True, blank=True)
    tags = models.ForeignKey(Tags, on_delete=models.CASCADE, verbose_name='Тег')

    def __str__(self):
        return str(self.news)

    class Meta:
        verbose_name = 'Тег новости'
        verbose_name_plural = 'Теги новости'
        db_table = 'tags_news'
        permissions = [
            ("can_add_tags", "Может добавлять теги к новостям"),
        ]


