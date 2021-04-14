from django.urls import path
from shop import views
from .views import signupView, signinView, signoutView, add_to_wishlist, wishlist, view_profile , edit_profile, changePassword,dashboard_view

app_name = 'accounts'

urlpatterns = [
    path('create/', signupView, name='signup'),
    path('login/', signinView, name='signin'),
    path('logout/', signoutView, name='signout'),

    path('profile/', view_profile, name='view_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/password/', changePassword, name='change_password'),

    path('dashboard/', dashboard_view, name='dashboard_view'),

    path('wishlist', wishlist, name='wishlist'),
    path('wishlist/add_to_wishlist/<uuid:product_id>/', add_to_wishlist, name='user_wishlist'),
]