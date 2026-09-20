"""
URL configuration for inventory_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from inventory.views import dashboard, add_product, products,edit_product,delete_product,suppliers,reports, add_sale,sales_history,user_login,user_logout, register, profile, edit_profile, change_password, settings, stock_prediction, inventory_health, dead_stock, restock_suggestions, activity_timeline

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('add-product/', add_product, name='add_product'),
    path('products/',products,name='products'),
    path('edit-product/<int:id>/', edit_product, name='edit_product'),
    path('delete_product/<int:id>/', delete_product, name='delete_product'),
    path('suppliers/', suppliers, name='suppliers'),
    path('reports/', reports, name='reports'),
    path('add-sale/', add_sale, name='add_sale'),
    path('sales-history/', sales_history, name='sales_history'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('settings/', settings, name='settings'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('stock-prediction/', stock_prediction, name='stock_prediction'),
    path('inventory-health/', inventory_health, name='inventory_health'),
    path('dead-stock/', dead_stock, name='dead_stock'),
    path('restock-suggestions/', restock_suggestions, name='restock_suggestions'),
    path('activity-timeline/', activity_timeline, name='activity_timeline'),
]
