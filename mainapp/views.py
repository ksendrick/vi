from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

from django.utils.html import strip_tags

from authapp.forms import UserEditForm
from authapp.models import User
from mainapp.models import Image, Notification
from mainapp.signals import logger
from newsapp.models import News, Article
from recipesapp.models import Recipe, Favorite


def index(request):
    top_recipes = (
        Recipe.objects.annotate(favorite_count=Count('favorite'))
        .order_by('-favorite_count', '-created_at')
        [:4]
    )

    latest_news = News.objects.prefetch_related('tagsnews_set__tags').order_by('-created_at')[:5]
    relevant_articles = (
        Article.objects
        .filter(status='published')
        .prefetch_related('tagsnews_set__tags')
        .annotate(like_count=Count('likes'))
        .order_by('-like_count', '-created_at')
        [:4]
    )

    one_week_ago = timezone.now() - timedelta(days=7)

    top_authors = (
        User.objects.annotate(
            article_count=Count(
                'article',
                filter=Q(article__created_at__gte=one_week_ago, article__status='published')  # Added status filter
            )
        )
        .order_by('-article_count')[:3]
    )

    context = {
        'title': 'Кулинарный портал "Вкусные Исследования"',
        'top_recipes': top_recipes,
        'latest_news': latest_news,
        'relevant_articles': relevant_articles,
        'top_authors': top_authors,  # Add top_authors to the context
    }

    return render(request, 'mainapp/index.html', context)

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = Image(image=request.FILES['file'])
        image.save()
        return JsonResponse({'location': image.image.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_similar_recipes(recipe):
    ingredient_ids = recipe.ingredients.values_list('id', flat=True)

    similar_recipes = Recipe.objects.filter(ingredients__in=ingredient_ids).exclude(id=recipe.id).distinct()

    similar_recipes = similar_recipes.annotate(num_shared_ingredients=Count('ingredients')).order_by(
        '-num_shared_ingredients')

    return similar_recipes[:5]


def moderate_comment(comment, request):
    bad_words = ["кот", "помидор"]
    comment_text_lower = comment.text.lower()

    for word in bad_words:
        if word in comment_text_lower:
            comment.status = 'cancel'
            comment.save()

            if request.user.is_authenticated:
                messages.error(request, 'Ваш комментарий был отклонен, так как содержит запрещенные слова.')
            return False

    comment.status = 'published'
    comment.save()
    return True


COMMENT_STATUS_CHOICES = (
    ('news', 'Новая'),
    ('published', 'Опубликовано'),
    ('cancel', 'Отменена'),
)


@login_required
def profile(request):
    user = request.user
    article_status = request.GET.get('article_status', 'published')

    if article_status == 'draft':
        user_articles = Article.objects.filter(user=request.user, status='news')
    else:
        user_articles = Article.objects.filter(user=request.user, status=article_status)

    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    favorite_recipes_ids = Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True)
    liked_news = News.objects.filter(likes=request.user).order_by('-created_at')[:4]
    liked_articles = Article.objects.filter(likes=request.user).order_by('-created_at')[:4]

    recent_likes = sorted(
        list(liked_news) + list(liked_articles),
        key=lambda x: x.created_at,
        reverse=True
    )[:8]

    context = {
        'title': f"{user.first_name} {user.last_name}",
        'favorites': favorites,
        'favorites_count': favorites.count(),
        'favorite_recipes_ids': favorite_recipes_ids,
        'recent_likes': recent_likes,
        'recent_likes_count': len(recent_likes),
        'liked_news': liked_news,
        'liked_articles': liked_articles,
        'user_articles': user_articles,
        'user_articles_count': user_articles.count(),
        'article_status': article_status,
    }
    return render(request, 'mainapp/profile.html', context)


def profile_author(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    user_articles = Article.objects.filter(user=profile_user, status="published").order_by('-created_at')

    context = {
        'title': f"Профиль {profile_user.first_name} {profile_user.last_name}",
        'profile_user': profile_user,
        'user_articles': user_articles,
        'articles_count': user_articles.count(),
    }
    return render(request, 'mainapp/profile_user.html', context)


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)

    if not notification.is_read:
        notification.is_read = True
        notification.save()

    context = {
        'notification': notification,
        'title': f"{notification.message}",
    }
    return render(request, 'mainapp/notification_detail.html', context)


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('mainapp:notifications')  # Replace 'notifications_list' with the actual URL name of your notifications list view


@login_required
def notifications(request):
    user = request.user
    unread_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')

    read_notifications = Notification.objects.filter(
        user=user,
        is_read=True
    ).order_by('-created_at')
    notifications = list(unread_notifications) + list(read_notifications)
    unread_notifications_count = unread_notifications.count()

    context = {
        'title': 'Уведомления',
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'mainapp/notifications.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            email_changed = 'email' in form.changed_data

            user = form.save(commit=False)
            if email_changed:
                 form.email_changed = True
            user = form.save()


            if email_changed:
                try:
                    subject = 'Подтверждение нового email'
                    html_message = render_to_string('emails/email_confirmation.html', {
                        'user': user,
                        'code': user.email_confirmation_code
                    })
                    plain_message = strip_tags(html_message)
                    send_mail(
                        subject,
                        plain_message,
                        None,
                        [user.email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    return redirect('authapp:confirm_email')
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                    messages.error(request, 'Не удалось отправить письмо с подтверждением.')

            messages.success(request, 'Профиль успешно обновлен!')

            if form.has_changed() and 'password' in form.changed_data:
                update_session_auth_hash(request, request.user)
            return redirect('mainapp:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'mainapp/edit_profile.html', {
        'form': form,
        'title': 'Редактирование профиля'
    })

