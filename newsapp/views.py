
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.urls import reverse

from mainapp.forms import CommentForm
from mainapp.models import Comment, Notification
from .forms import ArticleForm, ArticleEditForm
from .models import News, TagsNews, Article, Tags
from django.http import HttpResponseRedirect


def index(request):
    news_list = News.objects.prefetch_related('tagsnews_set__tags', 'likes').all()

    sort_by = request.GET.get('sort', 'relevant')
    search_term = request.GET.get('search', '')
    tag_filter = request.GET.get('tag')

    if search_term:
        news_list = news_list.filter(name__icontains=search_term)

    if tag_filter:
        try:
            tag_id = int(tag_filter)
            news_list = news_list.filter(tagsnews__tags__id=tag_id)
        except ValueError:
            pass

    if sort_by == 'date':
        news_list = news_list.order_by('-created_at')
    elif sort_by == 'favorites':
        news_list = news_list.annotate(likes_count=Count('likes')).order_by('-likes_count')
    else:
        news_list = news_list.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')

    tags = Tags.objects.all()

    context = {
        'news_list': news_list,
        'title': 'Кулинарные новости',
        'sort_by': sort_by,
        'search_term': search_term,
        'tags': tags,
        'selected_tag': tag_filter
    }

    return render(request, 'newsapp/index.html', context)


def news_detail(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    tags_news = TagsNews.objects.filter(news=news)
    tags = [tn.tags for tn in tags_news]
    published_comments = Comment.objects.filter(
        news=news,
        parent_comment=None,
        status='published'
    ).order_by('-created_at')

    comment_form = CommentForm()

    for comment in published_comments:
        comment.published_replies = Comment.objects.filter(
            parent_comment=comment,
            status='published'
        ).order_by('created_at')
    total_comments = Comment.objects.filter(news=news, status='published').count()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('authapp:login')

        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.news = news
                new_comment.user = request.user
                parent_comment_id = request.POST.get('parent_comment')
                new_comment.status = 'news'

                if parent_comment_id:
                    try:
                        new_comment.parent_comment = Comment.objects.get(id=parent_comment_id)
                    except Comment.DoesNotExist:
                        new_comment.parent_comment = None
                new_comment.save()


                from mainapp.views import moderate_comment
                if not moderate_comment(new_comment, request):
                    total_comments = Comment.objects.filter(news=news, status='published').count()
                    return  redirect('newsapp:news_detail', news_id=news.id)

                total_comments = Comment.objects.filter(news=news, status='published').count()
                messages.success(request, 'Ваш комментарий успешно опубликован!')
                return redirect('newsapp:news_detail', news_id=news.id)

        elif 'like' in request.POST:
            if request.user.is_authenticated:
                if request.user in news.likes.all():
                    news.likes.remove(request.user)
                else:
                    news.likes.add(request.user)
                return redirect('newsapp:news_detail', news_id=news.id)
            else:
                return redirect('authapp:login')

    context = {
        'news': news,
        'tags': tags,
        'total_comments':total_comments,
        'comments': published_comments,
        'comment_form': comment_form,
        'is_liked': request.user in news.likes.all() if request.user.is_authenticated else False,
        'title': f"{news.name}",
    }
    return render(request, 'newsapp/news_detail.html', context)


def like_comment(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
    else:
        return redirect('authapp:login')

    return HttpResponseRedirect(
        reverse('newsapp:news_detail', args=[comment.news.id]) + '#comments'
    )

def like_comment_article(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
    else:
        return redirect('authapp:login')

    return HttpResponseRedirect(
        reverse('newsapp:article_detail', args=[comment.article.id]) + '#comments'
    )


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            return redirect('newsapp:add_tags', article_id=article.id)
    else:
        form = ArticleForm()

    return render(request, 'articles/article_form.html', {'form': form, 'title': 'Создание статьи'})


@login_required
def add_tags(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    all_tags = Tags.objects.all()
    selected_tags_ids = []

    if request.method == 'POST':
        selected_tags_ids = request.POST.getlist('tags')

        if not selected_tags_ids:
            messages.error(request, 'Пожалуйста, выберите хотя бы один тег.')
            current_tags = [tag_news.tags for tag_news in TagsNews.objects.filter(article=article)]
            current_tag_ids = [tag.id for tag in current_tags]

            context = {
                'article': article,
                'all_tags': all_tags,
                'current_tags': current_tags,
                'current_tag_ids': current_tag_ids,
                'title': 'Предварительный просмотр',
            }
            return render(request, 'articles/add_tags.html', context)  # Render the form again with the error

        TagsNews.objects.filter(article=article).delete()

        for tag_id in selected_tags_ids:
            tag = get_object_or_404(Tags, id=tag_id)
            TagsNews.objects.create(article=article, tags=tag)

        messages.success(request,
                         'Статья сохранена и ожидает проверки. Пожалуйста, не публикуйте её повторно - это может замедлить процесс модерации.')

        profile_url = reverse('mainapp:profile') + '?article_status=draft'
        return redirect(profile_url)

    current_tags = [tag_news.tags for tag_news in TagsNews.objects.filter(article=article)]
    current_tag_ids = [tag.id for tag in current_tags]

    context = {
        'article': article,
        'all_tags': all_tags,
        'current_tags': current_tags,
        'current_tag_ids': current_tag_ids,
        'title': 'Предварительный просмотр',
    }
    return render(request, 'articles/add_tags.html', context)

def article(request):
    article_list = Article.objects.filter(status='published')

    sort_by = request.GET.get('sort', 'relevant')
    search_term = request.GET.get('search', '')
    tag_filter = request.GET.get('tag')

    if search_term:
        article_list = article_list.filter(name__icontains=search_term)

    if tag_filter:
        try:
            tag_id = int(tag_filter)
            article_list = article_list.filter(tagsnews__tags__id=tag_id)
        except ValueError:
            pass

    if sort_by == 'date':
        article_list = article_list.order_by('-created_at')
    elif sort_by == 'favorites':
        article_list = article_list.annotate(likes_count=Count('likes')).order_by('-likes_count')
    else:
        article_list = article_list.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')

    tags = Tags.objects.all()

    context = {
        'article_list': article_list,
        'title': 'Статьи',
        'sort_by': sort_by,
        'search_term': search_term,
        'tags': tags,
        'selected_tag': tag_filter,
    }
    return render(request, 'articles/article.html', context)


def article_detail(request, article_id,notification_id=None):
    article = get_object_or_404(Article, pk=article_id)
    comment_form = CommentForm()
    total_comments = Comment.objects.filter(article=article, status='published').count()
    tags_article = TagsNews.objects.filter(article=article)
    tags = [tn.tags for tn in tags_article]

    if notification_id:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()

    published_comments = Comment.objects.filter(
        article=article,
        parent_comment=None,
        status='published'
    ).order_by('-created_at')

    for comment in published_comments:
        comment.published_replies = Comment.objects.filter(
            parent_comment=comment,
            status='published'
        ).order_by('created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('authapp:login')

        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                new_comment.user = request.user
                new_comment.status = 'news'

                parent_comment_id = request.POST.get('parent_comment')
                if parent_comment_id:
                    try:
                        new_comment.parent_comment = Comment.objects.get(id=parent_comment_id)
                    except Comment.DoesNotExist:
                        new_comment.parent_comment = None
                new_comment.save()


                from mainapp.views import moderate_comment
                if not moderate_comment(new_comment, request):

                    total_comments = Comment.objects.filter(article=article, status='published').count()
                    return redirect('newsapp:article_detail', article_id=article.id)

                total_comments = Comment.objects.filter(article=article, status='published').count()
                messages.success(request, 'Ваш комментарий успешно опубликован!')
                return redirect('newsapp:article_detail', article_id=article.id)



        elif 'like' in request.POST:
            if request.user.is_authenticated:
                if request.user in article.likes.all():
                    article.likes.remove(request.user)
                else:
                    article.likes.add(request.user)
                return redirect('newsapp:article_detail', article_id=article.id)
            else:
                return redirect('authapp:login')

    context = {
        'article': article,
        'comments': published_comments,
        'comment_form': comment_form,
        'is_liked': request.user in article.likes.all() if request.user.is_authenticated else False,
        'total_comments': total_comments, # Добавлено total_comments
        'title': f"{article.name}",
        'tags':tags,
    }
    return render(request, 'articles/article_detail.html', context)


@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, user=request.user)
    
    if request.method == 'POST':
        form = ArticleEditForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect(reverse('mainapp:profile') + '?article_status=draft')
    else:
        form = ArticleEditForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'title': 'Редактирование статьи'
    }
    return render(request, 'articles/edit_article.html', context)