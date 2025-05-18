from django.contrib import messages
from django.db.models import Count

from mainapp.forms import CommentForm
from mainapp.models import Comment
from recipesapp.models import Category, Kitchen
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeSteps, IngredientRecipe, Favorite
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q


def index(request):
    categories = Category.objects.all()
    kitchens = Kitchen.objects.all()
    recipes = Recipe.objects.all()

    sort_by = request.GET.get('sort', 'relevant')
    category_filter = request.GET.get('category')
    kitchen_filter = request.GET.get('kitchen')
    search_term = request.GET.get('search', '')

    recipes = recipes.annotate(favorites_count=Count('favorite', distinct=True))

    if category_filter:
        try:
            category_id = int(category_filter)
            recipes = recipes.filter(category__id=category_id)
        except ValueError:
            pass

    if kitchen_filter:
        try:
            kitchen_id = int(kitchen_filter)
            recipes = recipes.filter(kitchen__id=kitchen_id)
        except ValueError:
            pass

    if search_term:
        recipes = recipes.filter(
            Q(ingredientrecipe__ingredient__name__icontains=search_term) |
            Q(name__icontains=search_term)
        ).distinct()

    if sort_by == 'date':
        recipes = recipes.order_by('-id')
    elif sort_by == 'favorites':
        recipes = recipes.order_by('-favorites_count')
    else:
        recipes = recipes.order_by('-favorites_count', '-id')

    total_recipes = Recipe.objects.count()
    title = f'Сборник рецептов ({total_recipes})'

    if request.user.is_authenticated:
        favorite_recipes_ids = Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True)
    else:
        favorite_recipes_ids = []

    context = {
        'title': title,
        'recipes': recipes,
        'categories': categories,
        'kitchens': kitchens,
        'selected_category': category_filter,
        'selected_kitchen': kitchen_filter,
        'sort_by': sort_by,
        'search_term': search_term,
        'no_recipes_found': not recipes.exists(),
        'favorite_recipes_ids': favorite_recipes_ids,
    }

    return render(request, 'recipesapp/index.html', context)

@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user

    try:
        favorite = Favorite.objects.get(user=user, recipe=recipe)
        favorite.delete()
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=user, recipe=recipe)

    return redirect('recipesapp:index')


@login_required
def toggle_favorite_profile(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user

    try:
        favorite = Favorite.objects.get(user=user, recipe=recipe)
        favorite.delete()
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=user, recipe=recipe)

    return redirect('mainapp:profile')



def recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe_steps = RecipeSteps.objects.filter(recipe=recipe)
    ingredient_recipes = IngredientRecipe.objects.filter(recipe=recipe)

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(recipe=recipe, user=request.user).exists()
    else:
        is_favorite = False

    published_comments = Comment.objects.filter(
        recipe=recipe,
        parent_comment=None,
        status='published'
    ).order_by('-created_at')

    comment_form = CommentForm()

    for comment in published_comments:
        comment.published_replies = Comment.objects.filter(
            parent_comment=comment,
            status='published'
        ).order_by('created_at')

    total_favorites = Favorite.objects.filter(recipe=recipe).count()
    total_comments = Comment.objects.filter(recipe=recipe, status='published').count()
    similar_recipes = get_similar_recipes(recipe)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('authapp:login')

        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.recipe = recipe
                new_comment.user = request.user
                new_comment.status = 'news'

                parent_comment_id = request.POST.get('parent_comment')
                if parent_comment_id:
                    try:
                        parent_comment = Comment.objects.get(id=parent_comment_id)

                        if parent_comment.status == 'published':
                            new_comment.parent_comment = parent_comment
                        else:

                            new_comment.parent_comment = None
                    except Comment.DoesNotExist:
                        new_comment.parent_comment = None

                new_comment.save()

                from mainapp.views import moderate_comment
                if not moderate_comment(new_comment, request):

                    total_comments = Comment.objects.filter(recipe=recipe, status='published').count()
                    return redirect('recipesapp:recipe', recipe_id=recipe.id)

                total_comments = Comment.objects.filter(recipe=recipe, status='published').count()
                messages.success(request, 'Ваш комментарий успешно опубликован!')
                return redirect('recipesapp:recipe', recipe_id=recipe.id)

        elif 'favorite' in request.POST:
            if is_favorite:
                Favorite.objects.filter(recipe=recipe, user=request.user).delete()
                total_favorites = Favorite.objects.filter(recipe=recipe).count()
            else:
                Favorite.objects.create(recipe=recipe, user=request.user)
                total_favorites = Favorite.objects.filter(recipe=recipe).count()
            is_favorite = Favorite.objects.filter(recipe=recipe, user=request.user).exists()
            return redirect('recipesapp:recipe', recipe_id=recipe.id)

    context = {
        'title': f"{recipe.name} рецепт",
        'recipe': recipe,
        'recipe_steps': recipe_steps,
        'ingredient_recipes': ingredient_recipes,
        'is_favorite': is_favorite,
        'comments': published_comments,
        'comment_form': comment_form,
        'total_favorites': total_favorites,
        'total_comments': total_comments,
        'similar_recipes': similar_recipes,
    }
    return render(request, 'recipesapp/recipe.html', context)



def get_similar_recipes(recipe):
    similar_recipes = []
    recipes_in_same_category = Recipe.objects.filter(category=recipe.category).exclude(pk=recipe.pk)

    print(f"Рецепты в той же категории: {[r.name for r in recipes_in_same_category]}")

    name_words = set(recipe.name.lower().split())
    for other_recipe in recipes_in_same_category:
        other_name_words = set(other_recipe.name.lower().split())
        common_words = name_words.intersection(other_name_words)

        if common_words:
            recipe_url = reverse('recipesapp:recipe', args=[other_recipe.pk])
            similar_recipes.append((other_recipe.name, recipe_url, len(common_words)))

    similar_recipes.sort(key=lambda x: x[2], reverse=True)
    similar_recipes = [(name, url) for name, url, _ in similar_recipes]

    print(f"Похожие рецепты: {similar_recipes}")

    return similar_recipes


def like_comment(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
    else:
        return redirect('authapp:login')

    return HttpResponseRedirect(reverse('recipesapp:recipe', args=[comment.recipe.id]))
