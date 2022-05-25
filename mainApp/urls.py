from django.urls import path

from . import views

urlpatterns = [
    path('', views.Login, name = "Login"),  # elbyt7tt '' hnaa kan elerror
    # path('Register/',views.Register,name="Register"),
    path('Result/', views.Result, name="Result"),
    path('Home/', views.Home, name="Home"),
    path('New-Patiant/', views.New, name="New-Patiant"),
    path('Search/', views.Search, name="Search")
]
