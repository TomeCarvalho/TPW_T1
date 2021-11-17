from django.shortcuts import render
from app.models import Product

from itertools import zip_longest

# Create your views here.
def index(request):
    return render(request, 'layout.html')


def dashboard(request):
    search_prompt = request.GET.get('search_prompt', '')
    if search_prompt:
        product_list = Product.objects.filter(name__icontains=search_prompt)
    else:
        product_list = Product.objects.all()
    print(product_list)
    pgs = zip_longest(*(iter(product_list),) * 3)  # chunky!
    print(pgs)
    tparams = {
        "three_page_group": pgs,
        "search_prompt": search_prompt[1:-1],
        #"logged": logged,
        "dashboardPage": True,
        #"user": User.objects.raw("SELECT * FROM app_user WHERE username = %s", params=[logged])
    }
    return render(request, "dashboard.html", tparams)


