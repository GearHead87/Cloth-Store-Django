from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from wishlist.models import WishlistItem
from django.db.models import Q
from .constants import COLOR

from wishlist.views import _wishlist_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages


def store(request, category_slug=None):
    categories = None
    products = None
    selected_color = request.GET.getlist('color')
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        
    filters = Q()
    if selected_color:
        color_filter = Q(color__in=selected_color)
        filters &= color_filter
        
    if min_price is not None and max_price is not None:
        price_filter = Q(price__gte=min_price, price__lte=max_price)
        filters &= price_filter
        
    products = products.filter(filters).order_by('price')
      
        
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'p_count': product_count,
        'selected_color': selected_color,
        'COLOR' : COLOR,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_wishlist = WishlistItem.objects.filter(wishlist__wishlist_id = _wishlist_id(request), product = single_product).exists()
    except Exception as e:
        raise e
        
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_wishlist'   : in_wishlist,
        'reviews': reviews,
    }
    return render(request, 'store/product_details.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            
            
# not work
# def store(request, category_slug=None):
#     categories = None
#     products = None
#     selected_color = request.GET.getlist('color')
    
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
    
#     if category_slug != None:
#         categories = get_object_or_404(Category, slug=category_slug)
#         products = Product.objects.filter(category=categories, is_available=True)
        
#     else:
#         products = Product.objects.all().filter(is_available=True).order_by('id')
        
#     if min_price is not None and max_price is not None and selected_color:
#         products = Product.objects.filter(color__in = selected_color, price__gte=min_price, price__lte=max_price).order_by('price')
        
#     if min_price is not None and max_price is not None:
#         products = Product.objects.filter(price__gte=min_price, price__lte=max_price).order_by('price')
        
#     if selected_color:
#         products = Product.objects.all().filter(color__in=selected_color)
        
#     paginator = Paginator(products, 6)
#     page = request.GET.get('page')
#     paged_products = paginator.get_page(page)
#     product_count = products.count()

#     context = {
#         'products': paged_products,
#         'p_count': product_count,
#         'selected_color': selected_color,
#         'COLOR' : COLOR,
#         'min_price': min_price,
#         'max_price': max_price,
#     }
#     return render(request, 'store/store.html', context)
