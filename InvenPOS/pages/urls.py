from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import authView, home, custom_login, admin_dashboard, cashier_dashboard, products
from django.urls import path
from . import views
from django.urls import path

urlpatterns = [
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path("login/", custom_login, name="login"),
    path("logout/", LogoutView.as_view(next_page='pages:login'), name="logout"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("products/", views.products, name="products"),
    path("cashier-dashboard/", cashier_dashboard, name="cashier_dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),

       path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/edit/<int:id>/", views.edit_product, name="edit_product"),
    path("products/delete/<int:id>/", views.delete_product, name="delete_product"),
      path('users/', views.users, name='users'),

path('products/restock/<int:id>/', views.restock_product, name='restock_product'),


   path('add-category/', views.add_category, name='add_category'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    
      path('users/', views.users, name='users'),
      path('suppliers/', views.suppliers, name='suppliers'),

path('add_supplier/', views.add_supplier, name='add_supplier'),
path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),

]