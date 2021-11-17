from django.contrib import admin
from app.models import Group, Client, Product, Sale, ProductInstance, ProductImage

admin.site.register(Group)
admin.site.register(Client)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(ProductInstance)
admin.site.register(ProductImage)