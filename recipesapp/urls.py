from django.urls import path
import recipesapp.views as recipesapp

app_name = 'recipesapp'

urlpatterns = [
    path('index/', recipesapp.index, name='index'),

    path('recipe/<int:recipe_id>/', recipesapp.recipe, name='recipe'),
    path('like_comment/<int:comment_id>/', recipesapp.like_comment, name='like_comment'),

    path('toggle_favorite/<int:recipe_id>/', recipesapp.toggle_favorite, name='toggle_favorite'),
    path('toggle_favorite_profile/<int:recipe_id>/', recipesapp.toggle_favorite_profile, name='toggle_favorite_profile'),

]
