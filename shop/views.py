from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator, EmptyPage , InvalidPage


def allProdCat(request, category_id=None):
    c_page = None
    products_list = None
    if category_id != None:
        c_page = get_object_or_404(Category, id=category_id)
        products_list = Product.objects.filter(category=c_page, available=True)
    else:
        products_list = Product.objects.all().filter(available=True)

    '''Pagination code'''
    paginator = Paginator(products_list, 3)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        products = paginator.page(page)
    except (EmptyPage,InvalidPage):
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/category.html', {'category':c_page, 'products':products})


def prod_detail(request,category_id,product_id):
    try:
        product = Product.objects.get(category_id=category_id, id=product_id)
    except Exception as e:
        raise e
    return render(request, 'shop/product.html',{'product':product})