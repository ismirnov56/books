from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BookReaderSerializer(ModelSerializer):
    """
    Сериализатор для читателей книг.
    """

    class Meta:
        """
        Модель пользователи сайта, поля ИФ
        """
        model = User
        fields = ('first_name', 'last_name')


class BooksSerializer(ModelSerializer):
    """
    Серилизатор для книг, с дополнительными полями, которые являются аннотацией для модели:
    - количество лайков
    - цена с учетом скидки
    - имя владельца
    - читали книги
    """
    count_likes = serializers.IntegerField(read_only=True)
    price_with_discount = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(read_only=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = (
            'id', 'name', 'price', 'author_name', 'owner_name', 'rating', 'price_with_discount', 'count_likes',
            'readers')


class UserBookRelationSerializer(ModelSerializer):
    """
    Сериализатор для оценки книги каждым пользователем
    """
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')
