from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm, PaymentForm
from django.shortcuts import render
from app.models import Group, Product, Sale, ProductInstance
from django.core.exceptions import ObjectDoesNotExist

from itertools import zip_longest

# Create your views here.


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(dashboard)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'logged': request.user.is_authenticated})


def dashboard(request):
    search_prompt = request.GET.get('search_prompt', '')
    if search_prompt:
        product_list = Product.objects.filter(name__icontains=search_prompt)
    else:
        product_list = Product.objects.all()
    pgs = zip_longest(*(iter(product_list),) * 3)  # chunky!
    tparams = {
        "logged": request.user.is_authenticated,
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1]
    }
    return render(request, "dashboard.html", tparams)


def myproducts(request):
    logged = request.user.is_authenticated
    if not logged:
        return redirect(dashboard)
    search_prompt = request.GET.get('search_prompt', '')
    if search_prompt:
        product_list = Product.objects.filter(name__icontains=search_prompt)
    else:
        product_list = Product.objects.all()
    print(product_list)
    pgs = zip_longest(*(iter(product_list),) * 3)  # chunky!
    print(pgs)
    tparams = {
        "logged": logged,
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1]
    }
    return render(request, "dashboard.html", tparams)


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


def cart(request):
    logged = request.user.is_authenticated
    if logged:
        product_instance_list = ProductInstance.objects.filter(client=request.user)
        products = []
        for product in product_instance_list:
            products.append(product.product)
        tparams = {
            "logged": logged,
            "products": products
        }
        return render(request, "cart.html", tparams)
    else:
        return redirect(dashboard)


def checkout(request):
    logged = request.user.is_authenticated
    if logged:
        if request.method == "POST":
            form = PaymentForm(request.POST)
            if form.is_valid():
                print("YEY")
                return redirect(dashboard)
            else:
                print("NEY")
        else:
            print("UH")
            form = PaymentForm()
        tparams = {
            "logged": logged,
            "form": form,
        }
        return render(request, "payment.html", tparams)
    else:
        return redirect(dashboard)




