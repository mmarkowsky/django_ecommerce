from distutils.command.upload import upload
from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=20, unique=True)
    description= models.CharField(max_length=255, blank=True)
    slug = models.CharField(max_length=100,unique=True)
    category_image = models.ImageField(upload_to="categories")

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name