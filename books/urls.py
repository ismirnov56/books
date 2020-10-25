from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, auth, UserBookRelationView


"""
Дабавление url на book и book_relation
"""

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/', include('store.urls')),
    path('auth/', auth)
]


"""
Добавление debug_toolbar для оптимизации
и просмотра запросов к бд с пмощью Django ORM.
"""
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
