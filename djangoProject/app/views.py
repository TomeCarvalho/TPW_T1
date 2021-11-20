from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm, PaymentForm, SearchForm, ProductForm
from django.shortcuts import render
from app.models import Group, Product, Sale, ProductInstance, ProductImage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q

from itertools import zip_longest


# Create your views here.
def index(request):
    return redirect(dashboard)


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
    search_prompt = ''
    if not logged:
        return redirect(dashboard)
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data.get('by_group')
            category = form.cleaned_data.get('by_category')
            upper = form.cleaned_data.get('by_price_Upper')
            lower = form.cleaned_data.get('by_price_Lower')
            q = Q(seller=request.user)

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
        search_prompt = request.GET.get('search_prompt', '')
        form = SearchForm()
        if search_prompt:
            product_list = Product.objects.filter(name__icontains=search_prompt, seller=request.user)
        else:
            product_list = Product.objects.filter(seller=request.user)
    pgs = zip_longest(*(iter(product_list),) * 3)  # chunky!
    tparams = {
        "logged": logged,
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1],
        "form": form,
        "my_products_page": True
    }
    return render(request, "dashboard.html", tparams)

def newproduct(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        print(request.POST)
        post = request.POST
        if form.is_valid():
            # processar dados e inserir na bd!
            category = form.cleaned_data['category']
            name = form.cleaned_data['name']
            stock = form.cleaned_data['stock']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            group = form.cleaned_data['group']
            img = form.cleaned_data['image']
            if group in [grp.name for grp in Group.objects.all()]:
                real_group = Group.objects.get(name=group)
            else:
                real_group = Group(name=group)
                real_group.save()
            new_product = Product(category=category,name=name,stock=stock,description=description,price=price,seller=request.user)
            new_product.save()
            new_product.group.add(real_group)
            image = ProductImage(url=img,product=new_product)
            image.save()
            return redirect(dashboard)
    else:
        form = ProductForm()

    return render(request, "newproduct.html", {
        "form": form,
        "logged": request.user.is_authenticated,
    })


def product_page(request, i):
    """Returns the page of the product with ID i if it exists, or an error page if not."""
    try:
        product = Product.objects.get(id=i)
        images = product.images
        groups = product.group.all()
        n = range(1, len(images))
        params = {
            'category': product.category.capitalize(),
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


NOT_ENOUGH_STOCK_MSG = 'The seller doesn\'t have enough of this product in stock at the moment.'
INVALID_QTY_MSG = 'Invalid quantity. It must be a positive number.'
ADDED_MSG = 'Product added to cart!'


@login_required
def add_to_cart(request):
    """Adds a product to the cart. Requires the user to be logged in."""
    if request.method == 'POST':
        product_id = request.POST['product_id']
        quantity = request.POST['quantity']
    else:  # If a sneaky user types it into the URL bar
        return redirect(dashboard)
    try:
        quantity = int(quantity)
    except ValueError:
        # messages.info(request, INVALID_QTY_MSG)
        print(f'ValueError with {product_id = }, {quantity = }')
        return redirect(dashboard)
    if quantity <= 0:
        # messages.info(request, INVALID_QTY_MSG)
        print(f'Invalid Quantity with {quantity = }')
        return redirect(dashboard)

    user = request.user
    product = Product.objects.get(id=product_id)
    try:  # Check if the user already has the product in their cart and thus is just increasing the quantity
        user_instance = ProductInstance.objects.get(client=user, product=product)
        if user_instance.quantity + quantity > product.stock:
            # messages.info(request, NOT_ENOUGH_STOCK_MSG)
            print(f'Not enough stock of {product.name} for {user.username} ({user_instance.quantity + quantity}/{product.stock})')
            return redirect(dashboard)
        user_instance.quantity += quantity
        user_instance.save()
        print(f'Increased quantity of {product} in {user}\'s cart by {quantity}')
    except ObjectDoesNotExist:
        if quantity > product.stock:
            # messages.error(request, NOT_ENOUGH_STOCK_MSG)
            return redirect(dashboard)
        ProductInstance(
            product=product,
            quantity=quantity,
            client=user,
            sold=False
        ).save()
        print(f'Instance of product {product} added to {user}\'s cart')
    # messages.info(request, 'Product added to cart!')
    return redirect(dashboard)


def cart(request):
    logged = request.user.is_authenticated
    if logged:
        product_instance_list = ProductInstance.objects.filter(client=request.user, sold=False)
        total = 0
        for product in product_instance_list:
            total += product.product.price * product.quantity
        tparams = {
            "logged": logged,
            "products": product_instance_list,
            "total": total
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
                print("ei")
                prod_insts = ProductInstance.objects.filter(client=request.user, sold=False)
                if any(prod_inst.quantity > prod_inst.product.stock for prod_inst in prod_insts):
                    return redirect(dashboard)  # TODO: handle this in a better fashion
                # TODO: figure out why the transaction number, total transaction price and payment method are missing
                sale = Sale(client=request.user, paymentMethod="Tmp Payment Method")  # TODO: get the payment method
                sale.save()
                for prod_inst in prod_insts:
                    product = prod_inst.product
                    product.stock -= prod_inst.quantity
                    prod_inst.sold = True
                    prod_inst.sale = sale
                    prod_inst.save()
                    product.save()
                sale.save()
                return redirect(dashboard)
            else:
                print("NEY")
        else:
            form = PaymentForm()
        tparams = {
            "logged": logged,
            "form": form,
        }
        return render(request, "payment.html", tparams)
    else:
        return redirect(dashboard)


@login_required
def history(request):
    """Returns the purchase and sale history of the user."""
    logged = request.user.is_authenticated
    user = request.user
    purchases = ProductInstance.objects.filter(client=user, sold=True).select_related()
    sales = ProductInstance.objects.filter(product__seller=user, sold=True).select_related()
    print(f'{purchases = }\n{sales = }')
    params = {
        'logged': logged,
        'purchases': purchases,
        'sales': sales
    }
    return render(request, 'history.html', params)
