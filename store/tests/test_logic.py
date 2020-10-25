from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
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

        UserBookRelation.objects.create(user=user1, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=self.book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=self.book_1, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.7', str(self.book_1.rating))
