from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Tag(models.Model):
    name = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    color = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='recipes/')
    tag = models.ManyToManyField(Tag)
    description = models.TextField()
    time = models.PositiveIntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
