from django.contrib import admin
# Register your models here.
from app.models import Group, Product, Sale, ProductInstance, ProductImage

admin.site.register(Group)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(ProductInstance)
admin.site.register(ProductImage)