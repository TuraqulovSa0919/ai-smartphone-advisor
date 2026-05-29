from django.urls import path
from .views import home, model_search, price_search, result_model_search, result_price_search,  login_view, profile_view, \
      logout_view, register_view, contact

urlpatterns = [
    path('', home, name="home_page"),
    path('model-search/', model_search, name='model_search_page'),
    path('search/result/', result_model_search, name='result_model_search_page'),
    path('price-search/', price_search, name='price_search_page'),
    path('price-search/result/', result_price_search, name='result_price_search_page'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile_page'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('contact/', contact, name='contact'),
]
