from django.urls import path
from . import views

app_name = 'convert'
urlpatterns = [
    path("login", views.Login.as_view(), name="login"),
    path("logout", views.Logout.as_view(), name="logout"),
    path('', views.IndexView.as_view(), name='index'),
    path('do/', views.do, name='do'),
    path('download/', views.download, name='download'),
    path('fileRemove/', views.fileRemove, name='fileRemove'),
]
