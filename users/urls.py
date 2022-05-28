from django.urls import path,re_path
from .views import *


urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('<int:pk>/', UserDetailView.as_view(), name='user'),
    path('user-roles/', GroupsView.as_view(),name='user-roles'),
    path('user-roles/<int:pk>/', GroupDetailView.as_view(),name="user-role"),

]