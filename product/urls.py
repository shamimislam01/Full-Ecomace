from django.urls import path
from . import views



urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/category/<int:category_id>/', views.product_category, name='product_category'),
    path('products/category/add/', views.product_category_add, name='product_category_add'),
    path('products/category/edit/<int:category_id>/', views.product_category_edit, name='product_category_edit'),
    path('products/category/delete/<int:category_id>/', views.product_category_delete, name='product_category_delete'),
    path('products/search/', views.product_search, name='product_search'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    
    # path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    # path('products/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    # path('products/<int:product_id>/remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    # path('products/<int:product_id>/add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    # path('products/<int:product_id>/remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    # path('products/<int:product_id>/add_review/', views.add_review, name='add_review'),
    # path('products/<int:product_id>/edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    # path('products/<int:product_id>/delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

]