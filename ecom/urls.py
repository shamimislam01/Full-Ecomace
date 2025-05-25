from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from product import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('home.urls')),
    path('', include('product.urls')),
    path('account/', include('account.urls')),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('orders/', include('orders.urls')),
    path('cart/', include('carts.urls')),
    


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)