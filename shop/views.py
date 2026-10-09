from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import Product, Order, OrderItem

def product_list(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    # Optional search filtering
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    return render(request, 'shop/product_list.html', {'products': products, 'query': query})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/product_detail.html', {'product': product})

# Authentication Views
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('shop:product_list')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                return redirect('shop:product_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

@require_POST
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('shop:product_list')

# Cart Views
def get_cart(request):
    return request.session.get('cart', {})

def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total_price = Decimal('0.00')
    
    # fetch products
    products = Product.objects.filter(id__in=cart.keys(), is_active=True)
    product_map = {str(p.id): p for p in products}
    
    # remove invalid items from cart (e.g. deactivated products)
    new_cart = {}
    
    for pid_str, quantity in cart.items():
        if pid_str in product_map:
            p = product_map[pid_str]
            # Adjust qty if it exceeds stock
            if quantity > p.stock:
                quantity = p.stock
                messages.warning(request, f"Quantity for {p.name} adjusted to available stock.")
            
            if quantity > 0:
                item_total = p.price * quantity
                total_price += item_total
                cart_items.append({
                    'product': p,
                    'quantity': quantity,
                    'item_total': item_total
                })
                new_cart[pid_str] = quantity
    
    if cart != new_cart:
        request.session['cart'] = new_cart
        request.session.modified = True

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@require_POST
def cart_add(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    quantity_str = request.POST.get('quantity', 1)
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            raise ValueError
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect('shop:product_detail', slug=product.slug)
    
    pid_str = str(product.id)
    current_quantity = cart.get(pid_str, 0)
    new_quantity = current_quantity + quantity
    
    if new_quantity > product.stock:
        messages.error(request, f"Cannot add {quantity}. Only {product.stock} available.")
    else:
        cart[pid_str] = new_quantity
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"Added {product.name} to your cart.")
        
    return redirect('shop:product_detail', slug=product.slug)

@require_POST
def cart_update(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    pid_str = str(product.id)
    
    if pid_str in cart:
        quantity_str = request.POST.get('quantity', 1)
        try:
            quantity = int(quantity_str)
            if quantity < 1:
                del cart[pid_str]
                messages.success(request, f"Removed {product.name} from your cart.")
            elif quantity > product.stock:
                messages.error(request, f"Only {product.stock} available for {product.name}.")
            else:
                cart[pid_str] = quantity
                messages.success(request, f"Updated quantity for {product.name}.")
        except ValueError:
            messages.error(request, "Invalid quantity.")
            
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('shop:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = get_cart(request)
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")
    return redirect('shop:cart_detail')

@login_required
def checkout_view(request):
    cart = get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('shop:cart_detail')
        
    products = Product.objects.filter(id__in=cart.keys(), is_active=True)
    product_map = {str(p.id): p for p in products}
    
    total_price = Decimal('0.00')
    cart_items = []
    
    for pid_str, quantity in cart.items():
        if pid_str in product_map:
            p = product_map[pid_str]
            if quantity > p.stock:
                messages.error(request, f"Not enough stock for {p.name}.")
                return redirect('shop:cart_detail')
            item_total = p.price * quantity
            total_price += item_total
            cart_items.append({'product': p, 'quantity': quantity})
            
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('delivery_address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        
        if not all([customer_name, email, phone, address, city, postal_code]):
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'total_price': total_price})
            
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    customer_name=customer_name,
                    email=email,
                    phone=phone,
                    delivery_address=address,
                    city=city,
                    postal_code=postal_code,
                    total_amount=total_price
                )
                
                for item in cart_items:
                    p = item['product']
                    qty = item['quantity']
                    
                    p.refresh_from_db()
                    if p.stock < qty:
                        raise ValueError(f"Insufficient stock for {p.name}")
                    
                    p.stock -= qty
                    p.save()
                    
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        product_name=p.name,
                        price=p.price,
                        quantity=qty
                    )
                    
                del request.session['cart']
                request.session.modified = True
                
                messages.success(request, f"Order {order.id} successfully placed.")
                return redirect('shop:order_history')
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('shop:cart_detail')
        except Exception as e:
            messages.error(request, "An error occurred while placing your order. Please try again.")
            return redirect('shop:cart_detail')

    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items')
    return render(request, 'shop/order_history.html', {'orders': orders})
