"""
URL configuration for OnlinerClone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from Clonliner import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('login/', views.customer_login, name='login'),
    path('customer_registration/', views.customer_registration, name='customer_registration'),
    path('logout/', views.customer_logout, name='logout'),
    path('chats/', views.chats, name='chats'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('market/', views.market, name='market'),
    path('market/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('open-chat/<int:user_id>/', views.open_chat, name='open_chat'),
    path('send-message/<int:chat_id>/', views.send_message, name='send_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
