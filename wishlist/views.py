from django.shortcuts import render,redirect,get_object_or_404
from .models import Wishlist, WishlistItem
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist

def add_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        is_wishlist_item_exists = WishlistItem.objects.filter(product=product,user=current_user).exists()
        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product = product, user = current_user)
            item = WishlistItem.objects.get(product=product, user=current_user)
            item.save()
        else:
            try:
                wishlist = Wishlist.objects.get(wishlist_id = _wishlist_id(request))
            except Wishlist.DoesNotExist:
                wishlist = Wishlist.objects.create(
                    wishlist_id = _wishlist_id(request)
                )
            wishlist.save()
            wishlist_item = WishlistItem.objects.create(
                product = product,
                wishlist = wishlist,
                user = current_user,
            )
            wishlist_item.save()
        return redirect('wishlist')
    
    else:
        return redirect('login')
    
    
def remove_wishlist_item(request,product_id, wishlist_item_id):
    product = get_object_or_404(Product, id = product_id)
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.get(product = product, user = request.user, id = wishlist_item_id )
    else:
        wishlist = Wishlist.objects.get(wishlist_id = _wishlist_id(request))
        wishlist_item = WishlistItem.objects.get(product = product, wishlist = wishlist, id= wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')
    
def wishlist(request, wishlist_items= None):
    try:
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user = request.user)
        else:
            wishlist = Wishlist.objects.get(wishlist_id = _wishlist_id(request))
            wishlist_items = WishlistItem.objects.filter(wishlist = wishlist)
            
    except ObjectDoesNotExist:
        pass
    
    context = {
        'wishlist_items' : wishlist_items
    }
    
    return render(request, 'wishlist/wishlist.html',context)