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
    # ex: /polls/5/
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # # ex: /polls/5/results/
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
]
