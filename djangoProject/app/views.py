from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm, PaymentForm, SearchForm
from django.shortcuts import render
from app.models import Group, Product, Sale, ProductInstance, ProductImage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q

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
    search_prompt = ''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            group = form.cleaned_data.get('by_group')
            category = form.cleaned_data.get('by_category')
            upper = form.cleaned_data.get('by_price_Upper')
            lower = form.cleaned_data.get('by_price_Lower')
            q = Q()
            if group:
                q &= Q(group__name=group)
            if category:
                q &= Q(category=category)
            if upper:
                q &= Q(price__lte=upper)
            if lower:
                q &= Q(price__gte=lower)
            product_list = Product.objects.filter(q)
    else:
        form = SearchForm()
        search_prompt = request.GET.get('search_prompt', '')
        if search_prompt:
            product_list = Product.objects.filter(name__icontains=search_prompt)
        else:
            product_list = Product.objects.all()



    pgs = zip_longest(*(iter(product_list),) * 3)  # chunky!
    tparams = {
        "logged": request.user.is_authenticated,
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1],
        "form": form
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
    """Returns the page of the product with ID i if it exists, or an error page if not."""
    try:
        product = Product.objects.get(id=i)
        images = product.images
        groups = product.group.all()
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
            'i': i,
            'groups': groups,
            'logged': request.user.is_authenticated
        }
        return render(request, 'product_page.html', params)
    except ObjectDoesNotExist:
        return render(request, 'product_page_error.html', {'i': i})


@login_required
def add_to_cart(request, product_id, quantity):
    """Adds a product to the cart. Requires the user to be logged in."""
    if quantity <= 0:
        messages.error(request, 'The quantity to add must be a positive number.')
    not_enough_stock_msg = 'The seller does\'nt have enough of this product in stock at the moment.'
    user = request.user
    product = Product.objects.get(id=product_id)
    try:  # Check if the user already has the product in their cart and thus is just increasing the quantity
        user_instance = ProductInstance.objects.get(client__user=user, product=product)
        if user_instance.quantity + quantity > product.stock:
            messages.error(request, not_enough_stock_msg)
            return
        user_instance.quantity += quantity
    except ObjectDoesNotExist:
        if quantity > product.stock:
            messages.error(request, not_enough_stock_msg)
            return
        ProductInstance(
            product=product,
            quantity=quantity,
            client=user
        ).save()
    messages.success(request, 'Product added to cart!')


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
