from django.core.validators import FileExtensionValidator
from django.db import models

from authapp.models import User
from newsapp.models import News, Article
from recipesapp.models import Recipe


class Image(models.Model):
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='article/%Y/%m/%d',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])],
        null=True
    )

    def __str__(self):
        return self.image.name


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='Ответ на комментарий')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    STATUS_CHOICES = [
        ('news', 'Новая'),
        ('published', 'Опубликовано'),
        ('canceled', 'Отменена'),
    ]
    status = models.CharField(verbose_name='Статус', choices=STATUS_CHOICES, default='news', max_length=20)

    def status_ru(self):
        status = dict(self.STATUS_CHOICES)
        return status.get(self.status, self.status)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        db_table = 'comment'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    message = models.CharField(max_length=255, verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)


    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        db_table = 'notifications'


    def __str__(self):
        return f"{self.user.username} - {self.message}"