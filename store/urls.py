from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationView

"""
создаем url для пользования API
"""
router = SimpleRouter()
router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = router.urls
