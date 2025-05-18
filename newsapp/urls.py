from django.urls import path
import newsapp.views as newsapp

app_name = 'newsapp'

urlpatterns = [
    path('index/', newsapp.index, name='index'),
    path('news/<int:news_id>/', newsapp.news_detail, name='news_detail'),
    path('like_comment/<int:comment_id>/', newsapp.like_comment, name='like_comment'),
    path('like_comment_article/<int:comment_id>/', newsapp.like_comment_article, name='like_comment_article'),
    path('article/create/', newsapp.article_create, name='article_create'),
    path('add_tags/<int:article_id>/', newsapp.add_tags, name='add_tags'),

    path('article_detail/<int:article_id>/', newsapp.article_detail, name='article_detail'),
    path('article/', newsapp.article, name='article'),

    path('article_detail/<int:article_id>/notification/<int:notification_id>/', newsapp.article_detail,
         name='article_detail_with_notification'),

    path('article/<int:article_id>/edit/', newsapp.edit_article, name='article_edit'),

]
