from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    color = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    title = models.CharField(
        max_length=200, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20, verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    title = models.CharField(max_length=50, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/')
    tag = models.ManyToManyField(Tag, verbose_name='Тэг')
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingridient,
                                         through='RecipeIngridient',
                                         through_fields=('recipe', 'ingridient'),
                                         verbose_name='Ингридиенты')
    time = models.PositiveIntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class RecipeIngridient(models.Model):
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='ingridients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.PositiveSmallIntegerField()


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower_recipe')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='following_recipe')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'follower {self.user} is following on {self.recipe}'


class FollowUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='author')

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'
