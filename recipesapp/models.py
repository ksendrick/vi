from django.core.validators import FileExtensionValidator
from django.db import models

from authapp.models import User

class Kitchen(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кухня'
        verbose_name_plural = 'Кухни'
        db_table = 'kitchen'


class Category(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'category'


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        db_table = 'ingredient'


class Recipe(models.Model):
    calories = models.IntegerField(verbose_name='Калории')
    proteins = models.IntegerField(verbose_name='Белки')
    fats = models.IntegerField(verbose_name='Жиры')
    carbohydrates = models.IntegerField(verbose_name='Углеводы')
    name = models.CharField(max_length=100, verbose_name='Название')
    desc = models.TextField(verbose_name='Описание')
    time = models.CharField(max_length=100, verbose_name='Время приготовления')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, verbose_name='Кухня')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)
    img = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe/%Y/%m/%d',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg', 'webp'])],
    )
    video = models.URLField(
        verbose_name='Ссылка на видео',
        max_length=200,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        db_table = 'recipe'


class RecipeSteps(models.Model):
    desc = models.TextField(verbose_name='Описание')
    img = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipeStep/%Y/%m/%d',
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg', 'webp'])],
        null=True
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    def __str__(self):
        return self.desc

    class Meta:
        verbose_name = 'Инструкция приготовления'
        verbose_name_plural = 'Инструкции приготовления'
        db_table = 'recipe_steps'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    weight = models.IntegerField(verbose_name='Количество', default=0)
    type = models.CharField(verbose_name='Тип', max_length=100)
    base_servings = models.IntegerField(verbose_name='Базовое количество порций', default=1)

    def __str__(self):
        return f"{self.recipe} - {self.ingredient}"

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        db_table = 'ingredient_recipe'


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return self.recipe

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        db_table = 'favorite'





