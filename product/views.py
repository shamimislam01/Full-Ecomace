from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ProductCategory, ProductReview
from django.shortcuts import render, get_object_or_404
from orders.models import OrderItem

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# def product_detail(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     review_count = product.reviews.count()
#     reviews = ProductReview.objects.all()
#     return render(request, 'product_detail.html', {
#         'product': product,
#         'review_count': review_count,
#         'reviews': reviews,
#     })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = ProductReview.objects.filter(product=product)  # এই লাইন বদলালাম
    review_count = reviews.count()  # এখানে শুধু ওই প্রোডাক্টের রিভিউ কাউন্ট হবে

    # এখানে আপনি যদি চান ব্যবহারকারী ওই প্রোডাক্ট কিনেছে কিনা তা চেক করতে, তাহলে has_purchased যোগ করতে পারেন
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'has_purchased': has_purchased,
    })


def submit_review(request, product_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')  # ✅ ঠিক নাম

        product = get_object_or_404(Product, id=product_id)

        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

        messages.success(request, 'Review submitted successfully!')
        return redirect('product_detail', slug=product.slug)

    return HttpResponse("Invalid request method.")









def product_category(request, category_id):
    products = Product.objects.filter(category_id=category_id, is_active=True).order_by('-created_at')
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product/product_category.html', {'page_obj': page_obj})

def product_search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query), is_active=True).order_by('-created_at')
    else:
        products = Product.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product/product_search.html', {'page_obj': page_obj, 'query': query})

def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category_id')
        image = request.FILES.get('image')

        product = Product.objects.create(
            name=name,
            slug=slug,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            image=image
        )
        messages.success(request, 'Product added successfully!')
        return redirect('product_list')
    return render(request, 'product/product_add.html')


def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.slug = request.POST.get('slug')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.category_id = request.POST.get('category_id')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('product_detail', product_id=product.id)
    return render(request, 'product/product_edit.html', {'product': product})


def product_category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        category = ProductCategory.objects.create(
            name=name,
            description=description
        )
        messages.success(request, 'Category added successfully!')
        return redirect('product_category', category_id=category.id)
    return render(request, 'product/product_category_add.html')


def product_category_edit(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('product_category', category_id=category.id)
    return render(request, 'product/product_category_edit.html', {'category': category})


def product_category_delete(request, category_id):

    category = get_object_or_404(ProductCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('product_list')
    return render(request, 'product/product_category_delete.html', {'category': category})











    
