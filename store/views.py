from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import UserBookRelation
from store.permissions import IsOwnerOrStaffReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer
from store.services.getqueryfromdb import get_books_with_annotate, get_user_book_relation


class BookViewSet(ModelViewSet):
    """
    View для работы с книгами
    Устанавливаем фильтрующие поля, поля поиска и сортировки.
    """
    queryset = get_books_with_annotate()
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffReadOnly]
    filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        """
        Присваиваем пользователю книги которые он создал
        """
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin,
                           GenericViewSet):
    """
    View для оценивания книнг.
    Каждый аутентифицированный пользователь может:
    - ставить лайк книге
    - добавлять в избраное
    - ставить оценку
    """
    permission_classes = [IsAuthenticated]
    queryset = get_user_book_relation()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                              book_id=self.kwargs['book'])
        return obj


def auth(request):
    '''
    аутентификация с помощью GitHub
    '''
    return render(request, 'oauth.html')
