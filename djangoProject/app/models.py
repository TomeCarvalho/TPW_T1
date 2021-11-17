from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=50)


class Client(models.Model):
    pass


class Product(models.Model):
    category = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    stock = models.IntegerField()
    image = models.URLField()
    description = models.CharField(max_length=300)
    price = models.FloatField()
    seller = models.ForeignKey(Client, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    paymentMethod = models.CharField(max_length=100)


class ProductInstance(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True)
