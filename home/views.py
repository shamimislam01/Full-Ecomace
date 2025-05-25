from django.shortcuts import render
from product.models import Product, ProductCategory, ProductReview

# Create your views here.


def index(request):
    products = Product.objects.all()
    reviews = ProductReview.objects.all()

    return render(request, 'index.html', {'products': products,'reviews': reviews}) 



def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)










