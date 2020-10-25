from django.contrib.auth.models import User
from django.test import TestCase

from store.services.getqueryfromdb import get_books_with_annotate, get_user_book_relation
from store.services.logic import set_rating
from store.models import Book, UserBookRelation


class SetRatingTestCase(TestCase):
    """
    Тестируем доп логику
    """
    def setUp(self) -> None:
        user1 = User.objects.create(username='test_user1', first_name='Ivan', last_name='Ivanov')
        user2 = User.objects.create(username='test_user2', first_name='Ivan', last_name='Sidorov')
        user3 = User.objects.create(username='test_user3', first_name='Ivan', last_name='Boboka')

        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 4', discount=10, owner=user1)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Author 1')

        UserBookRelation.objects.create(user=user1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=self.book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=self.book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user2, book=self.book_2, like=True, rate=4)

    def test_get_query(self):
        """
        Тестируем запросы к базе данных
        """
        queryset_books = get_books_with_annotate()
        queryset_book_relations = get_user_book_relation()
        self.assertEqual(2, queryset_books.count())
        self.assertEqual(5, queryset_book_relations.count())

    def test_ok(self):
        """
        Тестируем выставление оценок
        """
        set_rating(self.book_1)
        set_rating(self.book_2)
        self.book_1.refresh_from_db()
        self.book_2.refresh_from_db()
        self.assertEqual('4.7', str(self.book_1.rating))
        self.assertEqual('4.0', str(self.book_2.rating))
