"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tomogotchi import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name="login"),
    path('home/self', views.home, name="home"),
    path('home/<int:user_id>', views.visit, name="other-home"),
    path('edit', views.edit_furniture_page, name='edit'),
    path('test', views.test_html, name='test'),
    path('shop', views.shop, name='shop'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout', auth_views.logout_then_login, {"login_url" : "login"}, name='logout'),
    # path('edit-username/', auth_views.logout_then_login, name='logout'),
    path('get-item-picture/<str:name>', views.get_item_picture, name='get-item-picture'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)