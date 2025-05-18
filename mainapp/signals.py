from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from authapp.models import User
from mainapp.models import Notification, Comment
from newsapp.models import Article

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import random

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Article)
def create_notification_on_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_article = Article.objects.get(pk=instance.pk)
            if old_article.status != instance.status:
                if instance.status == 'published':
                    message = f'Ваша статья "{instance.name}" была опубликована'
                elif instance.status == 'canceled':
                    message = f'Ваша статья "{instance.name}" была отклонена'
                else:
                    message = f'Статус вашей статьи "{instance.name}" изменен'

                Notification.objects.create(
                    user=instance.user,
                    article=instance,
                    message=message
                )
        except Article.DoesNotExist:
            pass


@receiver(post_save, sender=Comment)
def create_notification_on_comment(sender, instance, created, **kwargs):
    if (created and instance.article and
            instance.status == 'published' and
            instance.user != instance.article.user):
        article = instance.article
        message = f'Пользователь {instance.user.username} оставил комментарий под вашей статьей "{article.name}"'

        Notification.objects.create(
            user=article.user,
            article=article,
            message=message
        )

@receiver(pre_save, sender=Article)
def send_email_on_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_article = Article.objects.get(pk=instance.pk)
            if old_article.status != instance.status:

                if (not hasattr(instance.user, 'email') or
                    not instance.user.email or
                    not instance.user.email_confirmed or
                    not instance.user.receive_notifications):
                    return

                try:
                    if instance.status == 'published':
                        subject = f'Ваша статья "{instance.name}" опубликована'
                        template = 'emails/article_published.html'
                    elif instance.status == 'canceled':
                        subject = f'Ваша статья "{instance.name}" отклонена'
                        template = 'emails/article_canceled.html'
                    else:
                        return

                    html_message = render_to_string(template, {
                        'article': instance,
                        'user': instance.user
                    })
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject,
                        plain_message,
                        None,
                        [instance.user.email],
                        html_message=html_message,
                        fail_silently=True
                    )

                except Exception as e:
                    logger.error(f"Failed to send status email: {str(e)}")

        except Article.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    # Игнорируем административную почту
    if instance.email == 'admin@admin.ru':
        return

    if created and instance.email:
        # Генерируем 6-значный код
        confirmation_code = str(random.randint(100000, 999999))
        instance.email_confirmation_code = confirmation_code
        instance.save()

        # Отправляем письмо с кодом
        try:
            subject = 'Подтверждение email'
            html_message = render_to_string('emails/email_confirmation.html', {
                'user': instance,
                'code': confirmation_code
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject,
                plain_message,
                None,
                [instance.email],
                html_message=html_message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {instance.email}: {str(e)}")