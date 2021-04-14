from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import stripe
from order.models import Order, OrderItem
from vouchers.models import Voucher
from vouchers.forms import VoucherApplyForm
from decimal import Decimal

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
        cart_item.save()
    return redirect('cart:cart_detail')

def cart_detail(request, total=0, counter=0, cart_items = None):
    discount = 0
    voucher_id = 0
    new_total = 0
    voucher = None
    price = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = 'Homely Furniture Store - New order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY

    voucher_apply_form = VoucherApplyForm()

    try:
        voucher_id = request.session.get('voucher_id')
        voucher = Voucher.objects.get(id = voucher_id)
        if voucher != None:
            discount = (total*(voucher.discount/Decimal('100')))
            new_total = (total - discount)
            stripe_total = int(new_total * 100)
    except:
        ObjectDoesNotExist
        pass 

    if request.method == 'POST':
        print(request.POST)
        try:
            
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1'] 
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']
            customer = stripe.Customer.create(
                email = email,
                source = token)
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency = "eur",
                description = description,
                customer = customer.id)
            try:
                order_details = Order.objects.create(
                    token = token,
                    total = total,
                    emailAddress = email,
                    billingName = billingName,
                    billingAddress1 = billingAddress1,
                    billingCity = billingCity,
                    billingPostcode = billingPostcode,
                    billingCountry = billingCountry,
                    shippingName = shippingName,
                    shippingAddress1 = shippingAddress1,
                    shippingCity = shippingCity,
                    shippingPostcode = shippingPostcode,
                    shippingCountry = shippingCountry
                    )
                order_details.save()
                if voucher != None:
                    order_details.total = new_total
                    order_details.voucher = voucher
                    order_details.discount = discount
                order_details.save()
                for order_item in cart_items:
                    oi = OrderItem.objects.create(
                        product = order_item.product.name,
                        quantity = order_item.quantity,
                        price = order_item.product.price,
                        order = order_details
                        )
                    if voucher != None:
                        discount = (oi.price*(voucher.discount/Decimal('100')))
                        oi.price = (oi.price - discount)
                    else:
                        oi.price = oi.price*oi.quantity
                    oi.save
                    '''REDUCING THE STOCK ONCE THE ORDER IS PLACED ! '''
                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()
                    '''ONCE ORDER IS SAVED TERMINAL WILL PRINT THIS MESSAGE'''
                    print('The Order has been created and stock has been updated')
                return redirect('order:thanks', order_details.id)
            except ObjectDoesNotExist:
                pass
                
        except stripe.error.CardError as e:
            return false, e
            
    return render(request, 'cart.html', {'cart_items':cart_items, 'total':total, 'counter':counter,
                                          'data_key':data_key, 'stripe_total':stripe_total,
                                          'description':description, 'voucher_apply_form': voucher_apply_form , 'new_total': new_total,
                                          'voucher':voucher, 'discount':discount})

def cart_remove(request, product_id):
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart:cart_detail')

def full_remove(request, product_id):
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
        return redirect('cart:cart_detail')