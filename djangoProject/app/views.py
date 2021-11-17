from django.shortcuts import render
from app.models import Group, Client, Product, Sale, ProductInstance
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    return render(request, 'layout.html')


def product_page(request, i):
    try:
        product = Product.objects.get(id=i)
        images = product.productimage_set.all()
        n = range(1, len(images))
        params = {
            'category': product.category,
            'name': product.name,
            'stock': product.stock,
            'images': images,
            'n': n,
            'description': product.description,
            'price': product.price,
            'seller': product.seller,
            'i': i
            # TODO: groups
        }
        return render(request, 'product_page.html', params)
    except ObjectDoesNotExist:
        return render(request, 'product_page_error.html', {'i': i})
